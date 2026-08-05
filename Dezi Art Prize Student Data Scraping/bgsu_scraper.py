import argparse
import csv
import os
import re

URL = "https://scholarworks.bgsu.edu/ms_art/"
CACHE_PATH = os.path.join("..", "cache", "bgsu", "ms_art.html")

YEAR_HEADING_RE = re.compile(r'<h3 id="year_(\d{4})">')
ARTICLE_RE = re.compile(
    r'<p class="article-listing"><a href="([^"]*)"[^>]*>([^<]*)</a>,\s*([^<]*)</p>'
)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_students(html, target_year):
    # Find the target year's <h3> heading, then take everything up to the
    # next <h3 id="year_..."> heading (or end of document) as that year's
    # section.
    heading_positions = [(m.start(), m.group(1)) for m in YEAR_HEADING_RE.finditer(html)]
    start = end = None
    for i, (pos, year) in enumerate(heading_positions):
        if year == target_year:
            start = pos
            end = heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(html)
            break
    if start is None:
        return []

    segment = html[start:end]

    students = []
    for record_url, title, author in ARTICLE_RE.findall(segment):
        author = author.strip()
        title = title.strip()
        if not author:
            continue
        students.append({
            "name": author,
            "email": "",
            "major": "MFA Studio Art",
            "graduation_year": target_year,
            "portfolio_url": record_url.strip(),
            "college": "BGSU",
            "notes": f"Thesis title: \"{title}\"; no email/personal portfolio published "
                     "on source page (portfolio_url is the ScholarWorks repository record)",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape BGSU ScholarWorks MFA thesis repository (most recent year)")
    parser.add_argument("--out", default="bgsu_students.csv")
    parser.add_argument("--year", default="2025", help="Year section to scrape (e.g. 2025)")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    html = fetch(URL, CACHE_PATH, force_refresh=args.force_refresh)
    students = parse_students(html, args.year)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    print(f"Wrote {len(students)} students ({args.year}) -> {args.out}")


if __name__ == "__main__":
    main()
