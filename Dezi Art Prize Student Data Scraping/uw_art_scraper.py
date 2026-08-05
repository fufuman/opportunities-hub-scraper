import argparse
import csv
import os
import re

URL = "https://henryart.org/exhibitions/2026-university-of-washington-mfa-mdes-thesis-exhibition"
CACHE_PATH = os.path.join("..", "cache", "uw_art", "henry_2026.html")

ARTISTS_RE = re.compile(r"<h4>Artists</h4>\s*<div class='indent'>(.*?)</div>", re.DOTALL)
NAME_ITEM_RE = re.compile(r"([^<]+?)(?:<br>|$)")


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
    m = ARTISTS_RE.search(html)
    if not m:
        return []

    names_html = m.group(1)
    names = [n.strip() for n in re.split(r"<br\s*/?>", names_html) if n.strip()]

    # This page lists all MFA + MDes cohort names together without mapping a
    # specific discipline to each individual — the surrounding text describes
    # the program collectively (New Genres, Painting + Drawing, 3D4M, MDes),
    # so we do not guess which discipline each name belongs to.
    return [{
        "name": name,
        "email": "",
        "major": "MFA/MDes (UW Art — discipline not specified per student)",
        "graduation_year": "2026",
        "portfolio_url": URL,
        "college": "University of Washington",
        "notes": "Name only, from Henry Art Gallery thesis exhibition page; "
                 "no email/portfolio published; source page does not map a "
                 "specific discipline to each individual student",
    } for name in names]


def main():
    parser = argparse.ArgumentParser(description="Scrape University of Washington 2026 MFA+MDes Thesis Exhibition (Henry Art Gallery)")
    parser.add_argument("--out", default="uw_art_students.csv")
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
