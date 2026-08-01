import argparse
import csv
import os
import re

URL = "https://www.bu.edu/cfa/featured-work/mfa-thesis-2024/"
CACHE_PATH = os.path.join("..", "cache", "bu", "mfa-thesis-2024.html")

PROGRAMS = [
    "MFA Painting",
    "MFA Sculpture",
    "MFA Visual Narrative",
    "MFA Print Media & Photography",
    "MFA Graphic Design",
]


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
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)
    text_plain = text_plain.replace("&amp;", "&")

    start = text_plain.find("Exhibiting Students by Program")
    end = text_plain.find("Faculty Advisors", start)
    segment = text_plain[start + len("Exhibiting Students by Program"):end]

    # Find each program heading's position within the segment, in order.
    positions = []
    for program in PROGRAMS:
        idx = segment.find(program)
        if idx != -1:
            positions.append((idx, program))
    positions.sort()

    students = []
    for i, (pos, program) in enumerate(positions):
        chunk_start = pos + len(program)
        chunk_end = positions[i + 1][0] if i + 1 < len(positions) else len(segment)
        names_blob = segment[chunk_start:chunk_end]
        names = [n.strip() for n in names_blob.split("•") if n.strip()]

        for name in names:
            students.append({
                "name": name,
                "email": "",
                "major": program,
                "graduation_year": "2024",
                "portfolio_url": URL,
                "college": "BU",
                "notes": "Name only, from 'Exhibiting Students by Program' list; "
                         "no email/portfolio published on source page",
            })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape BU College of Fine Arts 2024 MFA Thesis exhibitors")
    parser.add_argument("--out", default="bu_students.csv")
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

    from collections import Counter
    by_program = Counter(s["major"] for s in students)
    for program, count in by_program.items():
        print(f"  {program}: {count}")


if __name__ == "__main__":
    main()
