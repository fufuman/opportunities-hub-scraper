import argparse
import csv
import os
import re

CACHE_DIR = os.path.join("..", "cache", "pratt")
BASE_URL = "https://www.pratt.edu/events/"

# (url slug, major label, format: "clean" = "Exhibiting Artists:" comma list,
# "brk" = "Students featured:<br>"-delimited, ambiguous chunks)
PAGES = [
    ("pratt-shows-mfa-thesis-exhibition-part-1", "MFA Fine Arts", "clean"),
    ("pratt-shows-mfa-thesis-exhibition-part-2", "MFA Fine Arts", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-1", "BFA Painting", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-2", "BFA Painting", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-3", "BFA Painting", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-4", "BFA Painting", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-5", "BFA Painting", "clean"),
    ("pratt-shows-bfa-painting-thesis-week-6", "BFA Painting", "clean"),
    ("pratt-shows-bfa-drawing-thesis-week-1", "BFA Drawing", "clean"),
    ("pratt-shows-bfa-drawing-thesis-week-2", "BFA Drawing", "clean"),
    ("pratt-shows-bfa-drawing-thesis-week-3", "BFA Drawing", "clean"),
    ("pratt-shows-bfa-sculpture-and-integrated-practices-thesis-show", "BFA Sculpture and Integrated Practices", "clean"),
    ("pratt-shows-bfa-printmaking-thesis-show", "BFA Printmaking", "clean"),
    ("pratt-shows-photography-bfa-thesis-show-1", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-2", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-3", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-4", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-5", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-6", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-7", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-8", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-9", "BFA Photography", "brk"),
    ("pratt-shows-photography-bfa-thesis-show-10", "BFA Photography", "brk"),
    ("pratt-shows-photography-mfa-thesis-show-1", "MFA Photography", "brk"),
    ("pratt-shows-photography-mfa-thesis-show-2", "MFA Photography", "brk"),
]

# Names run from "Exhibiting Artists:" up to one of several known terminator
# phrases that follow on all observed pages (gallery/logistics info, the show
# title repeated, or the standard "Pratt Shows is a series..." boilerplate).
CLEAN_MARKER_RE = re.compile(
    r"Exhibiting Artists:\s*(.*?)"
    r"(?:Schafler Gallery|Dock 72|MFA Thesis Exhibition|Pratt Shows (?:is|are) a)"
)
BRK_MARKER_RE = re.compile(r"Students featured:((?:<br\s*/?>[^<]*)+)</p>")
BRK_ITEM_RE = re.compile(r"<br\s*/?>([^<]*)")


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


def parse_clean(html, major, source_url):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    m = CLEAN_MARKER_RE.search(text_plain)
    if not m:
        return []

    names_blob = m.group(1).replace(" and ", ", ")
    names = [n.strip() for n in names_blob.split(",") if n.strip()]

    students = []
    for name in names:
        students.append({
            "name": name,
            "email": "",
            "major": major,
            "graduation_year": "2026",
            "portfolio_url": source_url,
            "college": "Pratt",
            "notes": "Name only, from 'Exhibiting Artists' list; "
                     "no email/portfolio published on source page",
        })
    return students


def parse_brk(html, major, source_url):
    m = BRK_MARKER_RE.search(html)
    if not m:
        return []

    chunks = [c.strip() for c in BRK_ITEM_RE.findall(m.group(1)) if c.strip()]

    students = []
    for chunk in chunks:
        students.append({
            "name": chunk,
            "email": "",
            "major": major,
            "graduation_year": "2026",
            "portfolio_url": source_url,
            "college": "Pratt",
            "notes": "UNVERIFIED: source page lists 'Students featured' as <br>-separated "
                     "chunks that do not reliably align with individual name boundaries "
                     "(e.g. a name may be split across two chunks, or two names merged "
                     "into one); double-check against the source page before using",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Pratt Institute 2026 Pratt Shows thesis exhibitions")
    parser.add_argument("--out", default="pratt_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for slug, major, fmt in PAGES:
        url = BASE_URL + slug + "/"
        cache_path = os.path.join(CACHE_DIR, f"{slug}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)

        if fmt == "clean":
            students = parse_clean(html, major, url)
        else:
            students = parse_brk(html, major, url)

        print(f"{slug}: {len(students)} students ({'clean' if fmt == 'clean' else 'UNVERIFIED'})")
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
