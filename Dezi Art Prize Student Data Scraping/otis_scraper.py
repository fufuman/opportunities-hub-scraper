import argparse
import csv
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

INDEX_URL = "https://www.otis.edu/about/our-work/annual-exhibition/2026/all-students.html"
BASE_URL = "https://www.otis.edu"
CACHE_DIR = os.path.join("..", "cache", "otis")

STUDENT_LINK_RE = re.compile(
    r'<a class="cta" href="(?P<href>/about/our-work/annual-exhibition/2026/[^"]+/index\.html)">'
    r'(?P<name>[^<]*)</a>'
)
NAME_RE = re.compile(r'<div class="exhibitor-name-year">([^<]*)</div>')
DEPT_RE = re.compile(r'<div class="exhibitor-department">([^<]*)</div>')
EMAIL_RE = re.compile(r'class="exhibitor-email">.*?href="mailto:([^"]+)"', re.DOTALL)
PORTFOLIO_RE = re.compile(r'class="exhibitor-portfolio">.*?href="(https?://[^"]+)"', re.DOTALL)


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
    students = []
    for m in STUDENT_LINK_RE.finditer(html):
        href = m.group("href")
        if href in seen:
            continue
        seen.add(href)
        name = m.group("name").strip()
        if not name:
            continue
        slug = href.split("/")[-2]
        students.append({
            "name": name,
            "slug": slug,
            "url": BASE_URL + href,
        })
    return students


def slug_cache_path(slug):
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", slug)[:80]
    return os.path.join(CACHE_DIR, "students", f"{safe}.html")


def scrape_student_page(entry, force_refresh=False):
    cache_path = slug_cache_path(entry["slug"])
    try:
        html = fetch(entry["url"], cache_path, force_refresh=force_refresh)
    except Exception as exc:
        return {
            "name": entry["name"],
            "email": "",
            "major": "",
            "graduation_year": "2026",
            "portfolio_url": entry["url"],
            "college": "Otis",
            "notes": f"Fetch failed: {exc}",
        }

    name_m = NAME_RE.search(html)
    name = name_m.group(1).strip() if name_m else entry["name"]

    dept_m = DEPT_RE.search(html)
    major = dept_m.group(1).strip() if dept_m else ""

    email_m = EMAIL_RE.search(html)
    email = email_m.group(1).strip() if email_m else ""

    portfolio_m = PORTFOLIO_RE.search(html)
    portfolio_url = portfolio_m.group(1).strip() if portfolio_m else ""

    return {
        "name": name,
        "email": email,
        "major": major,
        "graduation_year": "2026",
        "portfolio_url": portfolio_url,
        "college": "Otis",
        "notes": "" if major else "Department not found on student page",
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape Otis College 2026 annual exhibition student list")
    parser.add_argument("--out", default="otis_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    index_cache = os.path.join(CACHE_DIR, "all-students.html")
    index_html = fetch(INDEX_URL, index_cache, force_refresh=args.force_refresh)
    entries = parse_student_index(index_html)
    print(f"Found {len(entries)} students in index")

    students = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = []
        for entry in entries:
            futures.append(pool.submit(scrape_student_page, entry, args.force_refresh))
            time.sleep(args.delay)

        for i, fut in enumerate(as_completed(futures), 1):
            try:
                students.append(fut.result())
            except Exception as exc:
                print(f"Worker error: {exc}")
            if i % 25 == 0:
                print(f"  ...{i}/{len(entries)} student pages processed")

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    missing_email = sum(1 for s in students if not s["email"])
    missing_major = sum(1 for s in students if not s["major"])
    missing_portfolio = sum(1 for s in students if not s["portfolio_url"])
    errors = sum(1 for s in students if "Fetch failed" in s["notes"])
    print(f"\nWrote {len(students)} students -> {args.out}")
    print(f"Missing email: {missing_email}, missing major: {missing_major}, "
          f"missing portfolio: {missing_portfolio}, fetch errors: {errors}")


if __name__ == "__main__":
    main()
