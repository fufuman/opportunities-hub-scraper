import argparse
import csv
import html
import os
import re
from datetime import date

PAGES = [
    ("https://www.bezalel.ac.il/en/department/arts/staff", "Fine Arts (BFA)"),
    ("https://www.bezalel.ac.il/en/department/ma/arts/staff", "Fine Arts (MFA)"),
    ("https://www.bezalel.ac.il/en/department/photography/staff", "Photography"),
]

CACHE_DIR = os.path.join("..", "cache", "bezalel_faculty")

CARD_SPLIT_RE = re.compile(r"(?=node--type-member)")
NAME_RE = re.compile(r'field--name-title[^>]*>([^<]+)</span>', re.DOTALL)
ROLE_RE = re.compile(r'field--name-field-role-in-department[^>]*>([^<]*)</div>', re.DOTALL)
EMAIL_RE = re.compile(r'field--name-field-email.*?mailto:([^"]+)"', re.DOTALL)
# course titles are the strongest medium signal for the Fine Arts pages, where
# the role-in-department field is mostly blank (only set for dept heads)
COURSES_BLOCK_RE = re.compile(
    r'field__label">Courses</div>\s*<div class=\'field__items\'>(.*?)</div>\s*</div>',
    re.DOTALL,
)
COURSE_ITEM_RE = re.compile(r'field__item">(?:<a[^>]*>)?([^<]+)', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["paint", "draw"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "screen based", "moving image"],
    "Photography": ["photo"],
    "Design": ["design", "visual communication", "industrial"],
    "UI/UX Design": ["interaction design", "ui", "ux", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft"],
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


def slugify(url):
    return re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")


def classify_medium(department_label, role_text, courses_text=""):
    haystack = f"{department_label} {role_text} {courses_text}".lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_faculty(page_html, source_url, department_label):
    faculty = []
    seen_emails = set()
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]  # drop preamble before first card
    # each split slice runs to EOF, not to the next card - truncate to just
    # this card's own content so a card missing a field can't accidentally
    # match a later card's name/role/email. Each slice starts with its own
    # "node--type-member" marker at index 0, so search from index 1 onward.
    cards = []
    for c in raw_cards:
        next_idx = c.find("node--type-member", 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        role_m = ROLE_RE.search(card)
        courses_m = COURSES_BLOCK_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        role = html.unescape(re.sub(r"\s+", " ", role_m.group(1) if role_m else "").strip())
        courses = [html.unescape(re.sub(r"\s+", " ", c).strip())
                   for c in COURSE_ITEM_RE.findall(courses_m.group(1))] if courses_m else []
        email = email_m.group(1).strip()
        if not name or not email:
            continue
        key = email.lower()
        if key in seen_emails:
            continue
        seen_emails.add(key)

        medium = classify_medium(department_label, role, " ".join(courses))
        if not medium:
            continue

        title = role or ", ".join(courses)
        faculty.append({
            "school_name": "Bezalel Academy of Arts and Design",
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
    parser = argparse.ArgumentParser(description="Scrape Bezalel Academy faculty emails")
    parser.add_argument("--out", default="bezalel_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    for url, department_label in PAGES:
        cache_path = os.path.join(CACHE_DIR, f"{slugify(url)}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url, department_label)
        print(f"{url}: {len(rows)} in-scope faculty")
        all_faculty.extend(rows)

    # BFA/MFA Fine Arts and Photography pages overlap on some cross-listed
    # faculty; keep one row per email, preferring whichever has more detail
    by_email = {}
    for row in all_faculty:
        key = row["email"].lower()
        existing = by_email.get(key)
        if existing is None or len(row["title"]) > len(existing["title"]):
            by_email[key] = row
    all_faculty = list(by_email.values())

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
