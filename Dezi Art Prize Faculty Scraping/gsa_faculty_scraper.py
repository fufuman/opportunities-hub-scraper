import argparse
import csv
import html
import os
import re
import time
from datetime import date

# The brief classified GSA as Tier 3 (no emails) based on /staff not showing
# emails on the listing page - correct, but individual profile pages DO
# publish a real email (e.g. "Email: N.Oddy@gsa.ac.uk"), just not on the
# listing itself. ~420 staff total across all departments (architecture,
# design history, admin, etc.) - only the ones whose job title names an
# in-scope medium are kept.
BASE_URL = "https://www.gsa.ac.uk/staff"
NUM_PAGES = 5  # ~420 total / ~100 per page, confirmed via pagination link on page 1

CACHE_DIR = os.path.join("..", "cache", "gsa_faculty")

CARD_SPLIT_RE = re.compile(r'(?=class="staffi-list-item)')
NAME_RE = re.compile(r'staff-name">([^<]+)</h6>', re.DOTALL)
TITLE_RE = re.compile(r'profile-title">([^<]*)</div>', re.DOTALL)
PROFILE_LINK_RE = re.compile(r'href="(/staff/[^"]+)" class="button', re.DOTALL)
EMAIL_RE = re.compile(r'Email:\s*([\w.+-]+@[\w.-]+\.\w+)', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewellery", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design", "product design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
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
        next_idx = c.find('class="staffi-list-item', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        link_m = PROFILE_LINK_RE.search(card)
        if not name_m or not link_m:
            continue
        title_m = TITLE_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1) if title_m else "").strip())
        profile_url = "https://www.gsa.ac.uk" + link_m.group(1)

        people.append({"profile_url": profile_url, "name": name, "title": title})
    return people


def main():
    parser = argparse.ArgumentParser(description="Scrape Glasgow School of Art staff emails")
    parser.add_argument("--out", default="gsa_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    all_people = []
    seen_urls = set()
    for page in range(1, NUM_PAGES + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}?f81c50ad_page={page}"
        cache_path = os.path.join(CACHE_DIR, f"staff_page{page}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_listing(page_html)
        new_rows = [r for r in rows if r["profile_url"] not in seen_urls]
        for r in new_rows:
            seen_urls.add(r["profile_url"])
        print(f"page {page}: {len(rows)} people ({len(new_rows)} new)")
        all_people.extend(new_rows)

    faculty = []
    for i, person in enumerate(all_people, start=1):
        medium = classify_medium(person["title"])
        if not medium:
            continue

        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        email_m = EMAIL_RE.search(profile_html)
        if not email_m:
            if not os.path.exists(profile_cache) or args.force_refresh:
                time.sleep(args.sleep)
            continue
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Glasgow School of Art",
            "faculty_name": person["name"],
            "title": person["title"],
            "department": "",
            "medium": medium,
            "email": email,
            "email_type": "profile",
            "source_url": person["profile_url"],
            "date_extracted": date.today().isoformat(),
        })
        print(f"  [{i}/{len(all_people)}] {person['name']}: {medium} ({email})")

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
