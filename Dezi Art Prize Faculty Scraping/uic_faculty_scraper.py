import argparse
import csv
import html
import os
import re
import time
from datetime import date

URL = "https://artandarthistory.uic.edu/content/art-faculty"
CACHE_DIR = os.path.join("..", "cache", "uic_faculty")

# section header -> medium bucket. Art Education excluded (out of scope per
# user's medium list); Emeriti has no medium of its own - classified per
# person from their listed title text instead, same as the other sections
# when title text is available.
SECTION_MEDIUM = {
    "Studio Arts": "Painting/Drawing",
    "Photography": "Photography",
    "New Media Arts": "UI/UX Design",
    "Moving Image": "Filmmaking",
    "Interdisciplinary Degree in the Arts": "",  # no single medium - classify from title
    "Emeriti": "",  # no single medium - classify from title
}

SECTION_HEADER_RE = re.compile(r'field-item even">([A-Za-z &]+?)\s*</div>')
# two markup variants appear on this page for a name+title pair:
#   <a href=".../profile/x">Name</a><br />Title
#   <div><a href=".../profile/x">Name</a></div><div>Title</div>
PERSON_RE = re.compile(
    r'<a href="([^"]*/profile/[^"]+)"[^>]*>([^<]+)</a>\s*'
    r'(?:<br\s*/?>\s*([^<]*)|</div>\s*<div>([^<]*)</div>)',
    re.DOTALL,
)
EMAIL_FIELD_RE = re.compile(r'field-name-field-email-id.*?mailto:([^"]+)"', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design", "new media"],
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


def classify_medium(title_text):
    haystack = title_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_listing(page_html):
    """Split the page by section headers, then extract (profile_url, name,
    title, section) for each person in an in-scope section."""
    parts = SECTION_HEADER_RE.split(page_html)
    people = []
    # parts alternates: [preamble, section1, content1, section2, content2, ...]
    for i in range(1, len(parts), 2):
        section = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        if section == "Art Education":
            continue
        for profile_url, name, title_a, title_b in PERSON_RE.findall(content):
            title = title_a or title_b
            people.append({
                "profile_url": profile_url if profile_url.startswith("http") else "https://artandarthistory.uic.edu" + profile_url,
                "name": html.unescape(re.sub(r"\s+", " ", name)).strip(),
                "title": html.unescape(re.sub(r"\s+", " ", title)).strip(),
                "section": section,
            })
    return people


def main():
    parser = argparse.ArgumentParser(description="Scrape UIC School of Art & Art History studio faculty emails")
    parser.add_argument("--out", default="uic_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0, help="seconds between profile fetches")
    args = parser.parse_args()

    listing_cache = os.path.join(CACHE_DIR, "art_faculty.html")
    listing_html = fetch(URL, listing_cache, force_refresh=args.force_refresh)
    people = parse_listing(listing_html)
    print(f"Listing: {len(people)} people in scope (Art Education excluded)")

    faculty = []
    for i, person in enumerate(people, start=1):
        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        email_m = EMAIL_FIELD_RE.search(profile_html)
        email = email_m.group(1).strip() if email_m else ""

        medium = SECTION_MEDIUM.get(person["section"], "") or classify_medium(person["title"])
        if not medium:
            continue
        if not email:
            continue

        faculty.append({
            "school_name": "University of Illinois Chicago, School of Art and Art History",
            "faculty_name": person["name"],
            "title": person["title"],
            "department": person["section"],
            "medium": medium,
            "email": email,
            "email_type": "profile",
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
