import argparse
import csv
import html
import os
import re
import time
from datetime import date

# The brief classified Yale as Tier 3 (no public emails) based on the
# /about/people/faculty-and-staff listing page, which is correct - no emails
# there. But each person links to their own profile page (art.yale.edu/<Name>)
# and SOME (not all - appears to be personal choice, several senior faculty
# link out to a personal site/Substack instead) publish a direct email there.
# Worth a full click-through pass rather than accepting the listing page's
# absence of emails as final.
URL = "https://www.art.yale.edu/about/people/faculty-and-staff"
CACHE_DIR = os.path.join("..", "cache", "yale_faculty")

# section header -> medium bucket. Administration/Staff and Faculty Governing
# Board excluded (not teaching roles); Academic Leadership and
# Interdepartmental/Undergraduate have no single medium of their own -
# classified per-person from their title text instead.
SECTION_MEDIUM = {
    "graphic design": "Design",
    "painting / printmaking": "Painting/Drawing",
    "photography": "Photography",
    "sculpture": "Sculpture",
    "academic leadership": "",
    "interdepartmental": "",
    "undergraduate": "",
    "yale norfolk school of art": "",
    "faculty emeriti": "",
}
EXCLUDED_SECTIONS = {"faculty governing board", "administration and staff"}

SECTION_HEADER_RE = re.compile(r'scrolling-list-module__title[^>]*>([^<]+)</h4>')
PERSON_RE = re.compile(r'<a href="(/[^"]+)">([^<]+)</a>,\s*([^<]*)</li>', re.DOTALL)
EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)
ADDR_RE = re.compile(r"([\w.+-]+@[\w.-]+\.\w+)")

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing", "printmaking"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "print media"],
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
    sections = SECTION_HEADER_RE.split(page_html)
    people = {}  # profile_url -> {name, title, section} - dedupe cross-listed people
    for i in range(1, len(sections), 2):
        section = sections[i].strip()
        section_key = section.lower()
        if section_key in EXCLUDED_SECTIONS:
            continue
        content = sections[i + 1] if i + 1 < len(sections) else ""

        for profile_path, name, title in PERSON_RE.findall(content):
            name = html.unescape(re.sub(r"\s+", " ", name)).strip()
            title = html.unescape(re.sub(r"\s+", " ", title)).strip()
            if profile_path not in people:
                people[profile_path] = {
                    "profile_url": "https://www.art.yale.edu" + profile_path,
                    "name": name,
                    "title": title,
                    "section": section_key,
                }
    return list(people.values())


def main():
    parser = argparse.ArgumentParser(description="Scrape Yale School of Art faculty emails (profile click-through)")
    parser.add_argument("--out", default="yale_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    listing_cache = os.path.join(CACHE_DIR, "faculty_staff.html")
    listing_html = fetch(URL, listing_cache, force_refresh=args.force_refresh)
    people = parse_listing(listing_html)
    print(f"Listing: {len(people)} unique people (Faculty Governing Board / Administration excluded)")

    faculty = []
    checked = 0
    for i, person in enumerate(people, start=1):
        section_medium = SECTION_MEDIUM.get(person["section"], "")
        medium = section_medium or classify_medium(person["title"])
        if not medium:
            continue

        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        checked += 1
        email_m = EMAIL_RE.search(profile_html)
        if not email_m:
            if not os.path.exists(profile_cache) or args.force_refresh:
                time.sleep(args.sleep)
            continue
        raw_email = html.unescape(email_m.group(1).strip())
        addr_m = ADDR_RE.search(raw_email)
        if not addr_m:
            if not os.path.exists(profile_cache) or args.force_refresh:
                time.sleep(args.sleep)
            continue
        email = addr_m.group(1)

        faculty.append({
            "school_name": "Yale School of Art",
            "faculty_name": person["name"],
            "title": person["title"],
            "department": person["section"],
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

    print(f"\nChecked {checked} in-scope profiles, {len(faculty)} had a public email -> {args.out}")


if __name__ == "__main__":
    main()
