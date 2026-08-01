import argparse
import csv
import os
import re

URL = ("https://students.colum.edu/ssac/exhibition-archives/Manifest-Exhibitions/"
       "2026/human-condition-2026-babfa-in-fine-art-exhibition")
CACHE_PATH = os.path.join("..", "cache", "columbia", "human-condition-2026.html")

GALLERY_RE = re.compile(
    r"<strong>([^<]+ Gallery)</strong>.*?Featuring works by:((?:<br\s*/?>[^<]+)+)",
    re.DOTALL,
)
NAME_ITEM_RE = re.compile(r"<br\s*/?>([^<]+)")


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
    for gallery, names_html in GALLERY_RE.findall(html):
        gallery = gallery.strip()
        for raw_name in NAME_ITEM_RE.findall(names_html):
            name = raw_name.strip()
            if not name:
                continue
            # Some names have odd internal letter-spacing in the source itself
            # (e.g. "Faith H o g a n", "Liz Z e r m e n o Robles") — kept
            # verbatim as published rather than guessed/"corrected", but
            # flagged since it looks like a typo/formatting artifact on
            # Columbia's own page, not an actual name.
            looks_letter_spaced = bool(re.search(r"\b\w(?: \w){2,}\b", name))
            notes = (f"Name only, from '{gallery}' exhibitor list on the Human Condition "
                     "2026 BA/BFA Fine Art Exhibition page; no email/portfolio published")
            if looks_letter_spaced:
                notes += ("; NOTE: name appears to have unusual letter-spacing in the "
                          "source HTML itself (e.g. single letters separated by spaces) "
                          "— kept verbatim, may not reflect the person's actual name spelling")
            students.append({
                "name": name,
                "email": "",
                "major": f"BFA/BA Fine Art ({gallery})",
                "graduation_year": "2026",
                "portfolio_url": URL,
                "college": "Columbia College Chicago",
                "notes": notes,
            })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Columbia College Chicago 2026 Human Condition BFA/BA Fine Art Exhibition")
    parser.add_argument("--out", default="columbia_students.csv")
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
