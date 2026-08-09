import argparse
import csv
import html
import os
import re
from datetime import date

BASE_URL = "https://arts.vcu.edu/directory/"

# (department query slug, department label, medium bucket). Slugs found via
# each department's own "Faculty" link on its landing page
# (arts.vcu.edu/department/<slug>/), not guessed.
DEPARTMENTS = [
    ("painting-printmaking", "Painting + Printmaking", "Painting/Drawing"),
    ("kinetic-imaging", "Kinetic Imaging", "2D/3D Animation"),
    ("sculpture-extended-media", "Sculpture + Extended Media", "Sculpture"),
    ("photography-film", "Photography + Film", "Photography"),
    ("communication-arts", "Communication Arts", "Design"),
    ("graphic-design", "Graphic Design", "Design"),
    ("craft-material-studies", "Craft and Material Studies", "Fiber and Material Arts"),
    ("fashion-design-merchandising", "Fashion Design and Merchandising", "Fashion"),
]

CACHE_DIR = os.path.join("..", "cache", "vcu_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<div class="people_list_item">)')
NAME_RE = re.compile(r'people_list_item_name_link"[^>]*>([^<]+)</a>', re.DOTALL)
TITLE_RE = re.compile(r'people_list_item_title">([^<]*)</span>', re.DOTALL)
EMAIL_RE = re.compile(r'detail_item email">.*?mailto:([^"]+)"', re.DOTALL)

# VCU's department directory pages mix teaching faculty with administrative/
# support staff under the same listing - exclude titles that are clearly not
# a teaching role rather than trying to positively match every faculty rank.
NON_FACULTY_TITLE_RE = re.compile(
    r"coordinator|administrative|manager|technician|advisor|"
    r"director of admissions|academic affairs|equipment and facilities",
    re.IGNORECASE,
)


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


def parse_faculty(page_html, source_url, department_label, medium):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="people_list_item">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        title_m = TITLE_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1) if title_m else "").strip())
        email = email_m.group(1).strip()

        if NON_FACULTY_TITLE_RE.search(title):
            continue

        faculty.append({
            "school_name": "Virginia Commonwealth University, School of the Arts (VCUarts)",
            "faculty_name": name,
            "title": title,
            "department": department_label,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape VCUarts faculty emails")
    parser.add_argument("--out", default="vcu_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for dept_slug, dept_label, medium in DEPARTMENTS:
        url = f"{BASE_URL}?department%5B%5D={dept_slug}"
        cache_path = os.path.join(CACHE_DIR, f"dir_{dept_slug}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url, dept_label, medium)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"{dept_label}: {len(rows)} faculty ({len(new_rows)} new)")
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
