import argparse
import csv
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

LIST_URL = "https://sva.edu/events/search/type/Exhibition"
BASE_URL = "https://sva.edu/events/"
CACHE_DIR = os.path.join("..", "cache", "sva")
TOTAL_LIST_PAGES = 22

CARD_RE = re.compile(
    r'href="/events/([a-z0-9-]+)" class="calendar-card">.*?'
    r'class="calendar-card-title">(?:<!---->)?\s*([^<]*?)\s*</div>'
    r'(?:<div class="calendar-card-departments">.*?<span class="department">([^<]*)</span>)?'
    r'.*?class="calendar-card-date">([^<]*)</div>',
    re.DOTALL,
)

NAME_LIST_RE = re.compile(
    r"(?:Exhibiting artists include|Artists include)\s*(.*?)"
    r"(?:\.\s+[A-Z“‘\"]|Link copied to clipboard|SHOW MORE|$)"
)
# The name list is often prefixed with a department/cohort description before
# the actual names start, e.g. "Exhibiting artists include BFA Visual and
# Critical Studies students Elsa Chen, ...". Strip anything up through the
# last occurrence of "student(s)" so only real names remain.
STUDENTS_PREFIX_RE = re.compile(r"^.*?\bstudents?\b\s+", re.IGNORECASE)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def slug_cache_path(subdir, slug):
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)[:100]
    return os.path.join(CACHE_DIR, subdir, f"{safe}.html")


def parse_list_page(html):
    entries = []
    for m in CARD_RE.finditer(html):
        slug, title, department, date_text = m.groups()
        entries.append({
            "slug": slug,
            "title": title.strip(),
            "department": (department or "").strip(),
            "date_text": date_text.strip(),
        })
    return entries


def is_2026(date_text):
    return "2026" in date_text


def scrape_event_page(entry, force_refresh=False):
    url = BASE_URL + entry["slug"]
    cache_path = slug_cache_path("events", entry["slug"])
    try:
        html = fetch(url, cache_path, force_refresh=force_refresh)
    except Exception as exc:
        return None

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    m = NAME_LIST_RE.search(text_plain)
    if not m:
        return []

    names_blob = m.group(1)
    names_blob = names_blob.lstrip(": ")
    names_blob = STUDENTS_PREFIX_RE.sub("", names_blob)
    # Trim to the last comma/"and" before any trailing sentence fragment that
    # slipped past the terminator lookahead.
    names_blob = names_blob.rstrip(". ")
    names_blob = names_blob.replace(" and ", ", ")

    # Parenthetical annotations like "(MFA 2019 Photography, Video and Related
    # Media)" contain their own commas, which would otherwise break a naive
    # comma-split. Mask commas inside parentheses before splitting, then
    # restore them so the whole parenthetical can be stripped as one unit.
    def _mask_commas(match):
        return match.group(0).replace(",", "\x00")

    masked = re.sub(r"\([^)]*\)", _mask_commas, names_blob)
    raw_names = [n.strip().rstrip(".").replace("\x00", ",") for n in masked.split(",") if n.strip()]

    students = []
    for name in raw_names:
        # Strip trailing parenthetical program/degree annotations, e.g.
        # "Paul Simon (MFA 2019 Photography, Video and Related Media)".
        clean_name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        if not clean_name:
            continue
        # Some pages list names space-separated with no commas at all (e.g. a
        # long list of ~20 names run together as one sentence); when that
        # happens this "name" ends up implausibly long and containing many
        # words. Skip rather than emit an unreliable merged blob.
        if len(clean_name.split()) > 5:
            continue
        students.append({
            "name": clean_name,
            "email": "",
            "major": entry["department"] or "SVA (program not specified on this page)",
            "graduation_year": "2026",
            "portfolio_url": url,
            "college": "SVA",
            "notes": f"Name only, from exhibition '{entry['title']}' description text; "
                     "no email/portfolio published on source page; exhibition may include "
                     "students, alumni, faculty, or guest artists together — not "
                     "confirmed to be current students only",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape SVA exhibition pages for 2026-dated student names")
    parser.add_argument("--out", default="sva_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--max-list-pages", type=int, default=TOTAL_LIST_PAGES)
    args = parser.parse_args()

    all_entries = []
    for page in range(1, args.max_list_pages + 1):
        url = f"{LIST_URL}?page={page}"
        cache_path = os.path.join(CACHE_DIR, "lists", f"page-{page}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)
        entries = parse_list_page(html)
        print(f"list page {page}: {len(entries)} events found")
        all_entries.extend(entries)

    entries_2026 = [e for e in all_entries if is_2026(e["date_text"])]
    print(f"\n{len(all_entries)} total events found across {args.max_list_pages} list pages")
    print(f"{len(entries_2026)} are 2026-dated, fetching those individual pages...")

    all_students = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = []
        for entry in entries_2026:
            futures.append(pool.submit(scrape_event_page, entry, args.force_refresh))
            time.sleep(args.delay)

        for i, fut in enumerate(as_completed(futures), 1):
            try:
                result = fut.result()
                if result:
                    all_students.extend(result)
            except Exception as exc:
                print(f"Worker error: {exc}")
            if i % 50 == 0:
                print(f"  ...{i}/{len(entries_2026)} event pages processed")

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    pages_with_names = len({s["portfolio_url"] for s in all_students})
    print(f"\nWrote {len(all_students)} students from {pages_with_names} exhibition pages -> {args.out}")


if __name__ == "__main__":
    main()
