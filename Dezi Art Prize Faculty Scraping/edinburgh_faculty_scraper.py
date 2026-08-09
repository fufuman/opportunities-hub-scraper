import argparse
import csv
import html
import os
import re
from datetime import date

BASE_URL = "https://www.eca.ed.ac.uk/people"
# filter to Academic Staff (17) + Key Academic Office Holders (16) only,
# excluding Honorary/Emeritus, Postgrad Research Students, Professional
# Services, and Student Representation - confirmed via the filter form's
# checkbox values on the unfiltered page, 2026-08-09
FILTER_QUERY = "field_people_type_target_id%5B17%5D=17&field_people_type_target_id%5B16%5D=16"
NUM_PAGES = 13  # confirmed via "Go to last page" -> page=12, 2026-08-09

CACHE_DIR = os.path.join("..", "cache", "edinburgh_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<a href="/profile/)')
NAME_RE = re.compile(r'staff-card__name[^>]*><span>([^<]+)</span>', re.DOTALL)
ROLE_RE = re.compile(r'staff-card__role[^>]*>([^<]*)</p>', re.DOTALL)
EMAIL_RE = re.compile(r'class="underline font-semibold"[^>]*>\s*([\w.+-]+@[\w.-]+\.\w+)\s*<', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "jewellery", "jewelry", "metal"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design", "product design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design", "computational design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design", "performance costume", "costume"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "fibre", "craft", "print media", "printmaking"],
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


def classify_medium(role_text):
    haystack = role_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_faculty(page_html, source_url):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<a href="/profile/', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        role_m = ROLE_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        role = html.unescape(re.sub(r"\s+", " ", role_m.group(1) if role_m else "").strip())
        email = email_m.group(1).strip()

        medium = classify_medium(role)
        if not medium:
            continue

        faculty.append({
            "school_name": "Edinburgh College of Art, University of Edinburgh",
            "faculty_name": name,
            "title": role,
            "department": role,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape Edinburgh College of Art faculty emails")
    parser.add_argument("--out", default="edinburgh_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for page in range(NUM_PAGES):
        url = f"{BASE_URL}?{FILTER_QUERY}&page={page}"
        cache_path = os.path.join(CACHE_DIR, f"filtered_page{page}.html")
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
