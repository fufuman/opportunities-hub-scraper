import argparse
import csv
import html
import os
import re
from datetime import date

BASE_URL = "https://art.utexas.edu/about/who-we-are/people"
NUM_PAGES = 5  # confirmed via pagination links (page=0..4) on page 0, 2026-08-09

CACHE_DIR = os.path.join("..", "cache", "ut_austin_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<div class="cofaprof__list teaser">)')
NAME_RE = re.compile(r'class="ut-link">([^<]+)</a>', re.DOTALL)
DESIGNATION_RE = re.compile(r'cofaprof-designation.*?field__item">([^<]*)</h4>', re.DOTALL)
EMAIL_RE = re.compile(r'cofaprof-email-address.*?mailto:([^"]+)"', re.DOTALL)
WBR_RE = re.compile(r"<wbr\s*/?>", re.IGNORECASE)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpture", "ceramic", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "print"],
}


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


def classify_medium(designation_text):
    haystack = designation_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_faculty(page_html, source_url):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="cofaprof__list teaser">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        designation_m = DESIGNATION_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        designation = html.unescape(re.sub(r"\s+", " ", designation_m.group(1) if designation_m else "").strip())
        # UT's markup inserts <wbr> tags mid-address for line-wrapping
        email = WBR_RE.sub("", email_m.group(1)).strip()

        medium = classify_medium(designation)
        if not medium:
            continue

        faculty.append({
            "school_name": "University of Texas at Austin, Department of Art and Art History",
            "faculty_name": name,
            "title": designation,
            "department": designation,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape UT Austin Dept of Art and Art History faculty emails")
    parser.add_argument("--out", default="ut_austin_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for page in range(NUM_PAGES):
        url = BASE_URL if page == 0 else f"{BASE_URL}?page={page}"
        cache_path = os.path.join(CACHE_DIR, f"people_page{page}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"page {page}: {len(rows)} in-scope faculty ({len(new_rows)} new)")
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
