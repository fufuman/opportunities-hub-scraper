import argparse
import csv
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HUB_URL = "https://amt.parsons.edu/finearts/"
CACHE_DIR = os.path.join("..", "cache", "parsons")

# (cohort slug, degree label, graduation year)
COHORTS = [
    ("2025-bfa-thesis", "BFA", "2025"),
    ("2025-mfa-thesis", "MFA", "2025"),
    ("2026-mfa-thesis", "MFA", "2026"),
]

# Nav/boilerplate pages and known placeholder entries that appear alongside
# real student slugs on the hub page — not actual students.
EXCLUDE_SLUGS = {
    "acknowledgments", "acknowledgements", "curators-note", "directors-note",
    "press-release", "test-artist", "2026-new-artist-name", "h",
}

NAME_H2_RE = re.compile(r'class="thesis title">\s*<h2>([^<]*)</h2>')
ARTIST_ENTRY_RE = re.compile(r'class="artist-entry">(.*?)<br', re.DOTALL)
LINK_RE = re.compile(r"href='([^']*)'")


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


def parse_cohort_slugs(hub_html, cohort_slug):
    pattern = re.compile(rf'href="[^"]*{re.escape(cohort_slug)}/([a-z0-9-]+)/"')
    slugs = sorted(set(pattern.findall(hub_html)))
    return [s for s in slugs if s not in EXCLUDE_SLUGS]


def slug_cache_path(cohort_slug, slug):
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", f"{cohort_slug}_{slug}")[:100]
    return os.path.join(CACHE_DIR, "students", f"{safe}.html")


def scrape_student_page(cohort_slug, degree, year, slug, force_refresh=False):
    url = f"https://amt.parsons.edu/finearts/{cohort_slug}/{slug}/"
    cache_path = slug_cache_path(cohort_slug, slug)
    try:
        html = fetch(url, cache_path, force_refresh=force_refresh)
    except Exception as exc:
        return {
            "name": slug.replace("-", " ").title(),
            "email": "",
            "major": f"{degree} Fine Arts",
            "graduation_year": year,
            "portfolio_url": url,
            "college": "Parsons",
            "notes": f"Fetch failed: {exc}",
        }

    name_m = NAME_H2_RE.search(html)
    name = name_m.group(1).strip() if name_m else slug.replace("-", " ").title()

    website = ""
    email = ""
    entry_m = ARTIST_ENTRY_RE.search(html)
    if entry_m:
        for href in LINK_RE.findall(entry_m.group(1)):
            href = href.strip()
            if href.lower().startswith("mailto:"):
                email = href[len("mailto:"):].strip()
            elif "instagram.com" not in href and not website:
                website = href

    return {
        "name": name,
        "email": email,
        "major": f"{degree} Fine Arts",
        "graduation_year": year,
        "portfolio_url": website or url,
        "college": "Parsons",
        "notes": "" if name_m else "Name not found on student page",
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape Parsons Fine Arts thesis cohorts (2025 BFA, 2025 MFA, 2026 MFA)")
    parser.add_argument("--out", default="parsons_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    hub_cache = os.path.join(CACHE_DIR, "hub.html")
    hub_html = fetch(HUB_URL, hub_cache, force_refresh=args.force_refresh)

    jobs = []
    for cohort_slug, degree, year in COHORTS:
        slugs = parse_cohort_slugs(hub_html, cohort_slug)
        print(f"{cohort_slug}: {len(slugs)} students found on hub page")
        for slug in slugs:
            jobs.append((cohort_slug, degree, year, slug))

    students = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = []
        for cohort_slug, degree, year, slug in jobs:
            futures.append(pool.submit(scrape_student_page, cohort_slug, degree, year, slug, args.force_refresh))
            time.sleep(args.delay)

        for i, fut in enumerate(as_completed(futures), 1):
            try:
                students.append(fut.result())
            except Exception as exc:
                print(f"Worker error: {exc}")
            if i % 25 == 0:
                print(f"  ...{i}/{len(jobs)} student pages processed")

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    missing_email = sum(1 for s in students if not s["email"])
    errors = sum(1 for s in students if "Fetch failed" in s["notes"])
    print(f"\nWrote {len(students)} students -> {args.out}")
    print(f"Missing email: {missing_email}, fetch errors: {errors}")

    from collections import Counter
    by_cohort = Counter((s["major"], s["graduation_year"]) for s in students)
    for (major, year), count in sorted(by_cohort.items()):
        print(f"  {major} {year}: {count}")


if __name__ == "__main__":
    main()
