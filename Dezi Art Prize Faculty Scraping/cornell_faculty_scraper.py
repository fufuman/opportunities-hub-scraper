import argparse
import csv
import html
import os
import re
import time
from datetime import date

URL = "https://aap.cornell.edu/art/art-people"
CACHE_DIR = os.path.join("..", "cache", "cornell_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<li class="people-list__item)')
NAME_RE = re.compile(r'people-list__person-link"\s*href="([^"]+)">([^<]+)</a>', re.DOTALL)
ROLE_RE = re.compile(r'people-list__person-role">\s*([^<]*?)\s*</p>', re.DOTALL)

EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)
BIO_RE = re.compile(r'person-topper__bio">(.*?)</div>\s*</div>', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
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


def slugify(url):
    return re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")


def classify_medium(role_text):
    haystack = role_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_listing(page_html):
    people = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<li class="people-list__item', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        if not name_m:
            continue
        role_m = ROLE_RE.search(card)

        profile_url = name_m.group(1).strip()
        name = html.unescape(re.sub(r"\s+", " ", name_m.group(2)).strip())
        role = html.unescape(re.sub(r"\s+", " ", role_m.group(1) if role_m else "").strip())

        people.append({"profile_url": profile_url, "name": name, "role": role})
    return people


def main():
    parser = argparse.ArgumentParser(description="Scrape Cornell AAP Art department faculty emails")
    parser.add_argument("--out", default="cornell_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0, help="seconds between profile fetches")
    args = parser.parse_args()

    listing_cache = os.path.join(CACHE_DIR, "art_people.html")
    listing_html = fetch(URL, listing_cache, force_refresh=args.force_refresh)
    people = parse_listing(listing_html)
    print(f"Listing: {len(people)} people")

    # the listing page repeats a handful of people (dual program listings,
    # etc.) - dedupe by profile URL before fetching
    seen_urls = set()
    unique_people = []
    for p in people:
        if p["profile_url"] in seen_urls:
            continue
        seen_urls.add(p["profile_url"])
        unique_people.append(p)
    people = unique_people

    faculty = []
    for i, person in enumerate(people, start=1):
        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        email_m = EMAIL_RE.search(profile_html)
        email = email_m.group(1).strip() if email_m else ""

        medium = classify_medium(person["role"])
        if not medium:
            bio_m = BIO_RE.search(profile_html)
            if bio_m:
                bio_text = re.sub(r"<[^>]+>", " ", bio_m.group(1))
                medium = classify_medium(bio_text)
        if not medium or not email:
            continue

        # imagetext@cornell.edu is a shared program mailbox that several
        # visiting/affiliated faculty list as their own contact - not a
        # personal address, flag it as such rather than "profile"
        email_type = "department_general" if email.lower() == "imagetext@cornell.edu" else "profile"

        faculty.append({
            "school_name": "Cornell University, Department of Art (AAP)",
            "faculty_name": person["name"],
            "title": person["role"],
            "department": "Art",
            "medium": medium,
            "email": email,
            "email_type": email_type,
            "source_url": person["profile_url"],
            "date_extracted": date.today().isoformat(),
        })
        print(f"  [{i}/{len(people)}] {person['name']}: {medium} ({email or 'no email'})")

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
