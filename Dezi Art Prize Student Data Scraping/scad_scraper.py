"""
SCAD Thesis Digital Collection scraper (library.scad.edu).

Plain static HTML, no JS rendering needed. Each program has its own saved
search URL (SEARCH=d:(...)), sorted newest-first (SORT=D). Since this
project scopes every school to the current/recent graduating cohort
(2025-2026), this scraper stops paginating a program as soon as it hits a
result dated 2024 or earlier -- results are sorted descending so nothing
newer follows.

Programs mapped to this project's 9 in-scope mediums:
  Painting -> Painting/Drawing        Illustration -> Painting/Drawing
  Printmaking -> Painting/Drawing     Sculpture -> Sculpture
  Fibers -> Fiber and Material Arts   Photography -> Photography
  Animation -> 2D/3D Animation        Film & Television -> Filmmaking
  Graphic Design -> Design            User Experience (UX) Design -> UI/UX Design
  Fashion -> Fashion
"""
import argparse
import csv
import os
import re
import subprocess
import time

CACHE_DIR = os.path.join("..", "cache", "scad")

PROGRAMS = {
    "Painting": ("Painting/Drawing", 'd:(%22 thesis painting%22)'),
    "Illustration": ("Painting/Drawing", 'd:(%22 thesis illustration%22)'),
    "Printmaking": ("Painting/Drawing", 'd:(%22 thesis printmaking%22)'),
    "Sculpture": ("Sculpture", 'd:(%22 thesis sculpture%22)'),
    "Fibers": ("Fiber and Material Arts", 'd:(%22 thesis fibers%22 )'),
    "Photography": ("Photography", 'd:(%22 thesis photography%22)'),
    "Animation": ("2D/3D Animation", 'd:(%22thesis animation%22)'),
    "Film & Television": ("Filmmaking", 'd:(%22 thesis film%22)'),
    "Graphic Design": ("Design", 'd:(%22 thesis graphic design%22)+or+(%22 thesis graphic Design and Visual Experience%22)'),
    "User Experience (UX) Design": ("UI/UX Design", 'd:(%22 thesis user experience design%22)'),
    "Fashion": ("Fashion", 'd:(%22 thesis fashion%22)'),
}

BASE = "https://library.scad.edu"
ENTRY_RE = re.compile(
    r'briefcitTitle">\s*<a[^>]*>([^<]*)</a>.*?'
    r'\n([^<]+?),\s*author\.<br',
    re.DOTALL,
)
YEAR_RE = re.compile(r"Savannah College of Art and Design,\s*(\d{4})")
ENTRY_BLOCK_RE = re.compile(r'<div class="briefcitRow">.*?<div class="briefcitClear">', re.DOTALL)
TITLE_RE = re.compile(r'briefcitTitle">\s*<a[^>]*>([^<]*)</a>')
AUTHOR_RE = re.compile(r"\n([^<\n]+?),\s*author\.<br")
YEAR_INLINE_RE = re.compile(r"Savannah College of Art and Design,\s*(\d{4})")
CAMPUS_RE = re.compile(r'"briefcitDetailMain">.*?<h2 class="briefcitTitle"', re.DOTALL)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    safe_url = url.replace(" ", "%20")
    result = subprocess.run(
        ["curl", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", safe_url],
        capture_output=True, timeout=30,
    )
    html = result.stdout.decode("utf-8", errors="replace")
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def parse_entries(html):
    """Return list of (title, author_lastfirst, year) for each result card."""
    entries = []
    for block in ENTRY_BLOCK_RE.findall(html):
        title_m = TITLE_RE.search(block)
        author_m = AUTHOR_RE.search(block)
        year_m = YEAR_INLINE_RE.search(block)
        if not title_m or not author_m or not year_m:
            continue
        entries.append((title_m.group(1).strip(), author_m.group(1).strip(), int(year_m.group(1))))
    return entries


def normalize_name(lastfirst):
    """'Bauer, Cherie Kuhn' -> 'Cherie Kuhn Bauer'."""
    if "," not in lastfirst:
        return lastfirst
    last, first = lastfirst.split(",", 1)
    return f"{first.strip()} {last.strip()}"


def scrape_program(program_name, min_year, force_refresh, sleep_s):
    medium, search_q = PROGRAMS[program_name]
    slug = re.sub(r"[^a-z0-9]+", "_", program_name.lower()).strip("_")
    results = []
    start = 1
    page_size = 50
    total = None
    page_num = 1
    while True:
        if start == 1:
            url = f"{BASE}/search/X?SEARCH={search_q}&SORT=D"
        else:
            total_str = total if total else 9999
            url = (f"{BASE}/search?/X{search_q}&SORT=D/X{search_q}&SORT=D"
                   f"&SUBKEY={search_q}/{start},{total_str},{total_str},E/2browse")
        cache_path = os.path.join(CACHE_DIR, f"{slug}_page{page_num}.html")
        html = fetch(url, cache_path, force_refresh)
        entries = parse_entries(html)
        if not entries:
            break

        if total is None:
            m = re.search(r"(\d+)\s*results?\s*found|,(\d+),(\d+),E/", html)
            total_m = re.search(r"/(\d+),(\d+),(\d+),E/", html)
            if total_m:
                total = int(total_m.group(2))

        stop = False
        for title, author, year in entries:
            if year < min_year:
                stop = True
                break
            results.append({
                "name": normalize_name(author),
                "major": f"{program_name} (SCAD)",
                "medium": medium,
                "graduation_year": year,
                "thesis_title": title,
            })

        print(f"  {program_name} page {page_num}: {len(entries)} entries, "
              f"{sum(1 for _, _, y in entries if y >= min_year)} in {min_year}+")

        if stop or len(entries) < page_size:
            break
        start += page_size
        page_num += 1
        time.sleep(sleep_s)

    return results


def main():
    parser = argparse.ArgumentParser(description="Scrape SCAD Thesis Digital Collection")
    parser.add_argument("--min-year", type=int, default=2025)
    parser.add_argument("--out", default="scad_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--programs", nargs="*", default=list(PROGRAMS.keys()))
    args = parser.parse_args()

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url",
                  "college", "notes", "sent_to_nitya"]

    all_rows = []
    seen = set()
    for program_name in args.programs:
        print(f"Scraping {program_name}...")
        results = scrape_program(program_name, args.min_year, args.force_refresh, args.sleep)
        for r in results:
            key = (r["name"].lower(), r["thesis_title"].lower())
            if key in seen:
                continue
            seen.add(key)
            all_rows.append({
                "name": r["name"],
                "email": "",
                "major": r["major"],
                "graduation_year": r["graduation_year"],
                "portfolio_url": "https://library.scad.edu/screens/theses.html",
                "college": "SCAD",
                "notes": f"Medium: {r['medium']}; thesis title '{r['thesis_title']}'; "
                         f"from SCAD Thesis Digital Collection (library.scad.edu), "
                         f"no email/portfolio published on source page",
                "sent_to_nitya": "",
            })

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"\nTotal unique students ({args.min_year}+): {len(all_rows)}")
    print(f"Saved -> {args.out}")


if __name__ == "__main__":
    main()
