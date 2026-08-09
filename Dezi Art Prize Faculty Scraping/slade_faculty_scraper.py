import argparse
import csv
import html
import os
import re
import time
from datetime import date

URL = "https://www.ucl.ac.uk/slade/people/academic/"
CACHE_DIR = os.path.join("..", "cache", "slade_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<h2 class="grid_item_title title">)')
LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*><span class="grid_item_title">([^<]+)</span></a>', re.DOTALL)
TITLE_RE = re.compile(r'grid_item_subtitle subtitle">(?:<span[^>]*>[^<]*</span>)?([^<]*)</div>', re.DOTALL)
EMAIL_RE = re.compile(r'mailto:([^"]+)"\s*class="email"', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewellery", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "fibre", "craft", "printmaking", "print media"],
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


def classify_medium(text):
    haystack = text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_listing(page_html):
    people = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<h2 class="grid_item_title title">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        link_m = LINK_RE.search(card)
        if not link_m:
            continue
        title_m = TITLE_RE.search(card)

        profile_path, name = link_m.groups()
        profile_url = "https://www.ucl.ac.uk" + profile_path if profile_path.startswith("/") else profile_path
        name = html.unescape(re.sub(r"\s+", " ", name).strip())
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1) if title_m else "").strip())

        people.append({"profile_url": profile_url, "name": name, "title": title})
    return people


def main():
    parser = argparse.ArgumentParser(description="Scrape Slade School of Fine Art (UCL) academic staff emails")
    parser.add_argument("--out", default="slade_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    listing_cache = os.path.join(CACHE_DIR, "academic.html")
    listing_html = fetch(URL, listing_cache, force_refresh=args.force_refresh)
    people = parse_listing(listing_html)
    print(f"Listing: {len(people)} academic staff")

    faculty = []
    for i, person in enumerate(people, start=1):
        medium = classify_medium(person["title"])
        if not medium:
            continue

        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        email_m = EMAIL_RE.search(profile_html)
        if not email_m:
            continue
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Slade School of Fine Art, University College London (UCL)",
            "faculty_name": person["name"],
            "title": person["title"],
            "department": "Slade School of Fine Art",
            "medium": medium,
            "email": email,
            "email_type": "profile",
            "source_url": person["profile_url"],
            "date_extracted": date.today().isoformat(),
        })
        print(f"  [{i}/{len(people)}] {person['name']}: {medium} ({email})")

        if not os.path.exists(profile_cache) or args.force_refresh:
            time.sleep(args.sleep)

    fieldnames = ["school_name", "faculty_name", "title", "department", "medium",
                  "email", "email_type", "source_url", "date_extracted"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in faculty:
            writer.writerow(row)

    print(f"\nWrote {len(faculty)} faculty -> {args.out}")


if __name__ == "__main__":
    main()
