import argparse
import csv
import html
import os
import re
from datetime import date

URL = "https://www.masongross.rutgers.edu/degrees-programs/art-design/faculty-staff/"
CACHE_PATH = os.path.join("..", "cache", "rutgers_faculty", "faculty_staff.html")

CARD_SPLIT_RE = re.compile(r'(?=<div class="name-text)')
NAME_RE = re.compile(r'name-text[^>]*>(.*?)</div>', re.DOTALL)
POSITION_RE = re.compile(r'pos-text[^>]*>(.*?)</div>', re.DOTALL)
DEPT_RE = re.compile(r'T-F6">([^<]*)</div>')
EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)
# a few hrefs are "mailto:Name%20%3Cemail%3E" (URL-encoded "Name <email>")
# rather than a bare address - pull the actual address out of either form
ADDR_RE = re.compile(r"([\w.+-]+@[\w.-]+\.\w+)")

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design", "in design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "printmaking", "print media"],
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


def classify_medium(text):
    haystack = text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_faculty(page_html, source_url):
    faculty = []
    seen_emails = set()
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="name-text', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        position_m = POSITION_RE.search(card)
        dept_m = DEPT_RE.search(card)

        name = html.unescape(re.sub("<[^>]+>", " ", name_m.group(1)))
        name = re.sub(r"\s+", " ", name).strip()
        position = html.unescape(re.sub("<[^>]+>", " ", position_m.group(1) if position_m else ""))
        position = re.sub(r"\s+", " ", position).strip()
        dept = html.unescape(re.sub(r"\s+", " ", dept_m.group(1) if dept_m else "").strip())
        raw_email = html.unescape(email_m.group(1).strip())
        addr_m = ADDR_RE.search(raw_email)
        if not addr_m:
            continue
        email = addr_m.group(1)

        key = email.lower()
        if key in seen_emails:
            continue
        seen_emails.add(key)

        medium = classify_medium(position)
        if not medium:
            continue

        faculty.append({
            "school_name": "Rutgers University, Mason Gross School of the Arts",
            "faculty_name": name,
            "title": position,
            "department": dept,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape Rutgers Mason Gross Art & Design faculty emails")
    parser.add_argument("--out", default="rutgers_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    page_html = fetch(URL, CACHE_PATH, force_refresh=args.force_refresh)
    faculty = parse_faculty(page_html, URL)

    fieldnames = ["school_name", "faculty_name", "title", "department", "medium",
                  "email", "email_type", "source_url", "date_extracted"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in faculty:
            writer.writerow(row)

    print(f"Wrote {len(faculty)} faculty -> {args.out}")


if __name__ == "__main__":
    main()
