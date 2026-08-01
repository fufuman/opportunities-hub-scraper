import argparse
import csv
import os
import re

CACHE_DIR = os.path.join("..", "cache", "yale")

# (url slug, department/major label, graduation year)
COHORTS = [
    ("spring-2025-painting-thesis", "Painting/Printmaking", "2025"),
    ("spring-2025-sculpture-thesis", "Sculpture", "2025"),
    ("spring-2025-photography-thesis", "Photography", "2025"),
    ("spring-2025-graphic-design-thesis", "Graphic Design", "2025"),
    ("spring-2026-painting-thesis", "Painting/Printmaking", "2026"),
    ("spring-2026-sculpture-thesis", "Sculpture", "2026"),
    ("spring-2026-photography-thesis", "Photography", "2026"),
    ("spring-2026-graphic-design-thesis", "Graphic Design", "2026"),
]

BASE_URL = "https://art.yale.edu/exhibitions/"


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


# Known phrases that follow the name list on Yale exhibition pages. Some names
# contain periods (e.g. "Z.T. Nguyen"), so we can't just split on the first ".".
TERMINATOR_RE = re.compile(
    r"\.\s*(?:Exhibition identity|Organized by|Public reception|Editor details|Learn more)"
)


def parse_students(html, major, year, source_url):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    idx = text_plain.find("Featuring")
    if idx == -1:
        return []

    segment = text_plain[idx:idx + 1500]
    term_m = TERMINATOR_RE.search(segment)
    names_blob = segment[:term_m.start()] if term_m else segment

    colon_idx = names_blob.find(":")
    if colon_idx != -1:
        names_blob = names_blob[colon_idx + 1:]
    else:
        names_blob = names_blob[len("Featuring"):]

    names_blob = names_blob.replace(" and ", ", ")
    names = [n.strip() for n in names_blob.split(",") if n.strip()]

    students = []
    for name in names:
        students.append({
            "name": name,
            "email": "",
            "major": f"MFA {major}",
            "graduation_year": year,
            "portfolio_url": source_url,
            "college": "Yale",
            "notes": "Name only, from exhibition 'Featuring' text; "
                     "no email/portfolio published on source page",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Yale School of Art MFA thesis exhibition rosters (2025-2026)")
    parser.add_argument("--out", default="yale_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for slug, major, year in COHORTS:
        url = BASE_URL + slug
        cache_path = os.path.join(CACHE_DIR, f"{slug}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)
        students = parse_students(html, major, year, url)
        print(f"{slug}: {len(students)} students")
        all_students.extend(students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    print(f"\nWrote {len(all_students)} students -> {args.out}")


if __name__ == "__main__":
    main()
