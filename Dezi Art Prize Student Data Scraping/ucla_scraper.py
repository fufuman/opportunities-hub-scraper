import argparse
import csv
import os
import re

URL = "https://www.art.ucla.edu/graduate-students"
CACHE_PATH = os.path.join("..", "cache", "ucla", "graduate-students.html")

SECTION_RE = re.compile(
    r'<h3 class="card-header">([^<]+)</h3>\s*<div class="card-body[^"]*">(.*?)</div>\s*</div>',
    re.DOTALL,
)
ITEM_RE = re.compile(
    r'<li class="mb-2">\s*(?:<a href="([^"]*)"[^>]*>([^<]*)</a>|([^<]+))\s*</li>',
    re.DOTALL,
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


def parse_students(html):
    students = []
    for area, body in SECTION_RE.findall(html):
        area = area.strip()
        for href, linked_name, plain_name in ITEM_RE.findall(body):
            name = (linked_name or plain_name).strip()
            name = re.sub(r"\s+", " ", name)
            if not name:
                continue
            students.append({
                "name": name,
                "email": "",
                "major": f"MFA {area}",
                "graduation_year": "",
                "portfolio_url": href.strip() if href else "",
                "college": "UCLA",
                "notes": "" if href else "No portfolio/social link listed for this student",
            })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape UCLA Department of Art current graduate students")
    parser.add_argument("--out", default="ucla_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    html = fetch(URL, CACHE_PATH, force_refresh=args.force_refresh)
    students = parse_students(html)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    missing_link = sum(1 for s in students if not s["portfolio_url"])
    print(f"Wrote {len(students)} students -> {args.out}")
    print(f"Missing portfolio link: {missing_link}")

    from collections import Counter
    by_area = Counter(s["major"] for s in students)
    for area, count in by_area.items():
        print(f"  {area}: {count}")


if __name__ == "__main__":
    main()
