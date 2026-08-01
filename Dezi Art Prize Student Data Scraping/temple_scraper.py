import argparse
import csv
import os
import re

URL = "https://tyler.temple.edu/2025-mfa-thesis-exhibitions-rewoven-collective-stories"
CACHE_PATH = os.path.join("..", "cache", "temple", "2025.html")

SCHEDULE_LINE_RE = re.compile(
    r'<strong>([^<]*?):?\s*</strong>\s*([^<]*?)(?:&nbsp;)?\s*(?:<br\s*/?>|</p>)'
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
    start = html.find("MFA Thesis Exhibitions schedule is as follows")
    end = html.find("Location:", start) if start != -1 else -1
    segment = html[start:end] if start != -1 and end != -1 else ""

    students = []
    for date_range, names_str in SCHEDULE_LINE_RE.findall(segment):
        names_str = names_str.replace("&nbsp;", " ").strip().rstrip(",")
        if not names_str:
            continue
        for raw_name in names_str.split(","):
            name = raw_name.strip()
            if not name:
                continue
            students.append({
                "name": name,
                "email": "",
                "major": "MFA Fine Arts",
                "graduation_year": "2025",
                "portfolio_url": "",
                "college": "Temple/Tyler",
                "notes": f"Name only, from exhibition schedule text (week: {date_range.strip()}); "
                         f"no email/major/portfolio published on source page",
            })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Temple/Tyler 2025 MFA Thesis student names")
    parser.add_argument("--out", default="temple_students.csv")
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

    print(f"Wrote {len(students)} students -> {args.out}")


if __name__ == "__main__":
    main()
