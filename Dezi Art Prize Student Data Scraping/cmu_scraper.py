import argparse
import csv
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

INDEX_URL = "https://art.cmu.edu/mfa/students/"
CACHE_DIR = os.path.join("..", "cache", "cmu")

STUDENT_LINK_RE = re.compile(r'href="(https?://art\.cmu\.edu/people/([a-z0-9-]+)/)"')
EXCLUDE_SLUGS = {"staff", "faculty", "head-of-school", "alumni"}

NAME_H2_RE = re.compile(r'<h2 class="entry-title">([^<]+)</h2>')
PAGE_CATEGORY_RE = re.compile(r'"pageCategory":\[([^\]]*)\]')
EMAIL_META_RE = re.compile(r'"email":"([^"]*)"')
WEBSITE_META_RE = re.compile(r'"personal_website":"([^"]*)"')

STAGE_LABELS = {
    "first-year-mfa": "First-Year MFA",
    "second-year-mfa": "Second-Year MFA",
    "third-year-mfa": "Third-Year MFA",
}


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


def parse_student_index(html):
    seen = set()
    entries = []
    for m in STUDENT_LINK_RE.finditer(html):
        url, slug = m.group(1), m.group(2)
        if slug in seen or slug in EXCLUDE_SLUGS:
            continue
        seen.add(slug)
        entries.append({"url": url, "slug": slug})
    return entries


def scrape_student_page(entry, force_refresh=False):
    cache_path = os.path.join(CACHE_DIR, "students", f"{entry['slug']}.html")
    try:
        html = fetch(entry["url"], cache_path, force_refresh=force_refresh)
    except Exception as exc:
        return {
            "name": entry["slug"].replace("-", " ").title(),
            "email": "",
            "major": "MFA Studio Art",
            "graduation_year": "",
            "portfolio_url": entry["url"],
            "college": "CMU",
            "notes": f"Fetch failed: {exc}",
        }

    name_m = NAME_H2_RE.search(html)
    name = name_m.group(1).strip() if name_m else entry["slug"].replace("-", " ").title()

    cat_m = PAGE_CATEGORY_RE.search(html)
    stage_label = ""
    if cat_m:
        cats = [c.strip().strip('"') for c in cat_m.group(1).split(",")]
        for cat in cats:
            if cat in STAGE_LABELS:
                stage_label = STAGE_LABELS[cat]
                break

    email_m = EMAIL_META_RE.search(html)
    email = email_m.group(1).strip() if email_m else ""

    website_m = WEBSITE_META_RE.search(html)
    website = website_m.group(1).strip() if website_m and website_m.group(1).strip() else entry["url"]

    major = f"MFA Studio Art ({stage_label})" if stage_label else "MFA Studio Art"

    return {
        "name": name,
        "email": email,
        "major": major,
        "graduation_year": "",
        "portfolio_url": website,
        "college": "CMU",
        "notes": "" if stage_label else "Class stage not found in page metadata",
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape CMU School of Art current MFA students")
    parser.add_argument("--out", default="cmu_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    index_cache = os.path.join(CACHE_DIR, "students_index.html")
    index_html = fetch(INDEX_URL, index_cache, force_refresh=args.force_refresh)
    entries = parse_student_index(index_html)
    print(f"Found {len(entries)} students in index")

    students = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = []
        for entry in entries:
            futures.append(pool.submit(scrape_student_page, entry, args.force_refresh))
            time.sleep(args.delay)

        for fut in as_completed(futures):
            try:
                students.append(fut.result())
            except Exception as exc:
                print(f"Worker error: {exc}")

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    missing_email = sum(1 for s in students if not s["email"])
    print(f"\nWrote {len(students)} students -> {args.out}")
    print(f"Missing email: {missing_email}")


if __name__ == "__main__":
    main()
