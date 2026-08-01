import argparse
import csv
import hashlib
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

INDEX_URL = "https://publications.risd.edu/grad-show-2026/student-index"
CACHE_DIR = os.path.join("..", "cache", "risd")

STUDENT_LINK_RE = re.compile(
    r'<a[^>]+href="(?P<href>/grad-show-2026/[^/"]+/?)"[^>]*>(?P<name>[^<]*)</a>'
)
H1_PROGRAM_RE = re.compile(
    r'<h1>[^<]*</h1><p>(?P<program>[^<]*)</p>'
)
SOCIALS_RE = re.compile(
    r'class="grad2026__student-socials[^"]*".*?<ul>(?P<links>.*?)</ul>',
    re.DOTALL,
)
LINK_RE = re.compile(r'<a href="([^"]*)"[^>]*>([^<]*)</a>')


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
    students = []
    for m in STUDENT_LINK_RE.finditer(html):
        href = m.group("href").rstrip("/")
        if href in ("/grad-show-2026/student-index", "/grad-show-2026/about"):
            continue
        name = m.group("name").strip()
        if not name:
            continue
        students.append({
            "name": name,
            "slug": href.split("/")[-1],
            "url": f"https://publications.risd.edu{href}",
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
            "college": "RISD",
            "notes": f"Fetch failed: {exc}",
        }

    program_m = H1_PROGRAM_RE.search(html)
    program = program_m.group("program").strip() if program_m else ""

    portfolio_url = ""
    socials_m = SOCIALS_RE.search(html)
    if socials_m:
        links = LINK_RE.findall(socials_m.group("links"))
        if links:
            # Prefer a non-Instagram/LinkedIn personal site if present, else first link.
            non_social = [href for href, label in links
                          if "instagram.com" not in href and "linkedin.com" not in href]
            portfolio_url = (non_social[0] if non_social else links[0][0]).strip()

    return {
        "name": entry["name"],
        "email": "",
        "major": program,
        "graduation_year": "2026",
        "portfolio_url": portfolio_url,
        "college": "RISD",
        "notes": "" if program else "Program not found on student page",
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape RISD Grad Show 2026 student index")
    parser.add_argument("--out", default="risd_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--delay", type=float, default=0.2, help="Seconds between request dispatches")
    args = parser.parse_args()

    index_cache = os.path.join(CACHE_DIR, "student-index.html")
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

    missing_major = sum(1 for s in students if not s["major"])
    missing_portfolio = sum(1 for s in students if not s["portfolio_url"])
    errors = sum(1 for s in students if "Fetch failed" in s["notes"])
    print(f"\nWrote {len(students)} students -> {args.out}")
    print(f"Missing major: {missing_major}, missing portfolio/social link: {missing_portfolio}, fetch errors: {errors}")


if __name__ == "__main__":
    main()
