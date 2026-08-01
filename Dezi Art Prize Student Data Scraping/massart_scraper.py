import argparse
import csv
import os
import re

CACHE_DIR = os.path.join("..", "cache", "massart")

PAGES = [
    ("https://calendar.massart.edu/event/2026-mfa-thesis-exhibition-PARTI", "part1"),
    ("https://calendar.massart.edu/event/2026-spring-mfa-thesis-exhibition-part-ii", "part2"),
]

FEATURED_RE = re.compile(r"FEATURED ARTISTS:\s*(.*?)(?:\.\s+[A-Z]|_{5,}|$)")
ENTRY_RE = re.compile(r"([^|]+?)\s*\|\s*(MFA[^A-Z]*(?:[A-Z][a-z/]*)*)")


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


def parse_students(html, source_url):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    m = FEATURED_RE.search(text_plain)
    if not m:
        return []
    segment = m.group(1)

    # Each entry is "Name | MFA Program" and entries run together with no
    # separator other than the next name starting right after the program
    # name ends. Split by looking for " | " boundaries and re-pairing.
    # Simplest reliable approach: split the whole segment on "|", then each
    # piece (except the first) starts with the program, and the next name is
    # appended at the end of that piece (since there's no delimiter between
    # "MFA Photography Anastasia Sierra" style runs). We instead match pairs
    # directly using a name-then-program pattern bounded by known program
    # labels.
    KNOWN_PROGRAMS = [
        "MFA Film/Video", "MFA Photography", "MFA Studio Arts",
        "MFA Fine Arts", "MFA 2D", "MFA 3D",
    ]
    pattern = re.compile(
        r"([A-Z][^|]*?)\s*\|\s*(" + "|".join(re.escape(p) for p in KNOWN_PROGRAMS) + r")"
    )

    students = []
    for name, program in pattern.findall(segment):
        name = name.strip()
        if not name:
            continue
        students.append({
            "name": name,
            "email": "",
            "major": program,
            "graduation_year": "2026",
            "portfolio_url": source_url,
            "college": "MassArt",
            "notes": "Name only, from 'FEATURED ARTISTS' list; "
                     "no email/portfolio published on source page",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape MassArt 2026 MFA Thesis Exhibition (Parts I & II)")
    parser.add_argument("--out", default="massart_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for url, label in PAGES:
        cache_path = os.path.join(CACHE_DIR, f"{label}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)
        students = parse_students(html, url)
        print(f"{label}: {len(students)} students")
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
