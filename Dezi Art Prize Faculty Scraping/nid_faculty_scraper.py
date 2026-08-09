import argparse
import csv
import html
import os
import re
from datetime import date

URL = "https://www.nid.ac.in/people/faculty"
CACHE_PATH = os.path.join("..", "cache", "nid_faculty", "faculty.html")

CARD_SPLIT_RE = re.compile(r'(?=<div class="faculty-info">)')
NAME_RE = re.compile(r'fac-name">([^<]+)</span>', re.DOTALL)
EMAIL_RE = re.compile(r'fac-email">([^<]*)</div>', re.DOTALL)
DESIG_RE = re.compile(r'fac-desig">([^<]*)</span>', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "animation film"],
    "Photography": ["photo"],
    "Design": ["industrial design", "product design", "communication design",
               "visual communication", "graphic design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design", "new media"],
    "2D/3D Animation": ["animation"],
    "Fashion": ["fashion", "apparel design"],
    "Fiber and Material Arts": ["textile", "weav", "fiber", "craft"],
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
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="faculty-info">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m or not email_m.group(1).strip():
            continue
        desigs = [html.unescape(re.sub(r"\s+", " ", d).strip())
                  for d in DESIG_RE.findall(card) if d.strip()]

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        email = email_m.group(1).strip()
        title = ", ".join(desigs)

        medium = classify_medium(title)
        if not medium:
            continue

        faculty.append({
            "school_name": "National Institute of Design (NID), Ahmedabad",
            "faculty_name": name,
            "title": title,
            "department": desigs[0] if desigs else "",
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape NID Ahmedabad faculty emails")
    parser.add_argument("--out", default="nid_faculty.csv")
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
