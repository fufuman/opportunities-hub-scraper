import argparse
import csv
import html
import os
import re
from datetime import date

BASE_URL = "https://www.rit.edu/artdesign/program-directory/"

# (program-directory id, program label, medium bucket). IDs found by fetching
# each program's landing page (/artdesign/study/<slug>) and reading its "All
# Program Faculty" link - not guessed. Programs with no faculty-directory link
# on their landing page (Furniture Design AOS, Photographic Arts Exploration,
# Studio Arts Exploration) are excluded. Art Education MST excluded as
# out-of-scope.
PROGRAMS = [
    ("411480", "3D Digital Design BFA", "2D/3D Animation"),
    ("411483", "Film and Animation BFA", "Filmmaking"),
    ("411486", "Graphic Design BFA", "Design"),
    ("411489", "Illustration BFA", "Painting/Drawing"),
    ("411492", "Industrial Design BFA", "Design"),
    ("411495", "Interior Design BFA", "Design"),
    ("411498", "Medical Illustration BFA", "Painting/Drawing"),
    ("411504", "New Media Design BFA", "UI/UX Design"),
    ("411507", "Photographic and Imaging Arts BFA", "Photography"),
    ("411510", "Photographic Sciences BS", "Photography"),
    ("411513", "Studio Arts BFA", "Painting/Drawing"),
    ("411456", "Ceramics MFA", "Sculpture"),
    ("411468", "Film and Animation MFA", "Filmmaking"),
    ("411387", "Fine Arts Studio MFA", "Painting/Drawing"),
    ("411459", "Furniture Design MFA", "Sculpture"),
    ("411453", "Glass MFA", "Sculpture"),
    ("411390", "Industrial Design MFA", "Design"),
    ("411462", "Metals and Jewelry Design MFA", "Sculpture"),
    ("411393", "Photography and Related Media MFA", "Photography"),
    ("411396", "Visual Communication Design MFA", "Design"),
]

CACHE_DIR = os.path.join("..", "cache", "rit_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<div class="pb-2 directory-name">)')
NAME_RE = re.compile(r'directory-name"><a[^>]*>([^<]+)</a>', re.DOTALL)
TITLE_RE = re.compile(r'directory-name">.*?directory-text-small">([^<]*)</div>', re.DOTALL)
DEPT_RE = re.compile(r'directory-department-description[^>]*>([^<]*)</div>', re.DOTALL)
EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        page_html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    return page_html


def parse_faculty(page_html, source_url, program_label, medium):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="pb-2 directory-name">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        title_m = TITLE_RE.search(card)
        dept_m = DEPT_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1) if title_m else "").strip())
        dept = html.unescape(re.sub(r"\s+", " ", dept_m.group(1) if dept_m else "").strip())
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Rochester Institute of Technology, College of Art and Design",
            "faculty_name": name,
            "title": title,
            "department": f"{dept} ({program_label})" if dept else program_label,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape RIT College of Art and Design faculty emails")
    parser.add_argument("--out", default="rit_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for program_id, program_label, medium in PROGRAMS:
        url = f"{BASE_URL}{program_id}"
        cache_path = os.path.join(CACHE_DIR, f"dir_{program_id}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url, program_label, medium)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"{program_label}: {len(rows)} faculty ({len(new_rows)} new)")
        all_faculty.extend(new_rows)

    fieldnames = ["school_name", "faculty_name", "title", "department", "medium",
                  "email", "email_type", "source_url", "date_extracted"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_faculty:
            writer.writerow(row)

    print(f"\nWrote {len(all_faculty)} faculty -> {args.out}")


if __name__ == "__main__":
    main()
