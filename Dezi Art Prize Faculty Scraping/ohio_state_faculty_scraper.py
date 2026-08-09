import argparse
import csv
import html
import os
import re
import time
from datetime import date

BASE_URL = "https://art.osu.edu"
DIRECTORY_URL = f"{BASE_URL}/people"
CACHE_DIR = os.path.join("..", "cache", "ohio_state_faculty")

IN_SCOPE_CATEGORIES = {"Chair, Faculty", "Faculty", "Associated Faculty", "Emeritus Faculty"}

CARD_SPLIT_RE = re.compile(r"(?=<div class=\"bux-person\">)")
PROFILE_LINK_RE = re.compile(r'<a class="bux-text-link" href="(/people/[^"]+)">\s*([^<]+?)\s*</a>', re.DOTALL)
DETAILS_RE = re.compile(r'bux-person__details">\s*<div><p>([^<]*)</p>', re.DOTALL)
EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["paint", "draw"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design", "art and technology"],
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


def slugify(path):
    return re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")


def classify_medium(text):
    haystack = text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_directory(page_html):
    """Return list of dicts: name, profile_url, title, email, category — for
    people in an in-scope category (Chair/Faculty/Associated/Emeritus Faculty,
    excluding Staff and Graduate Students)."""
    sections = re.split(r"<h2>([^<]+)</h2>", page_html)
    people = []
    for i in range(1, len(sections), 2):
        category = sections[i].strip()
        content = sections[i + 1] if i + 1 < len(sections) else ""
        if category not in IN_SCOPE_CATEGORIES:
            continue

        raw_cards = CARD_SPLIT_RE.split(content)[1:]
        cards = []
        for c in raw_cards:
            next_idx = c.find('<div class="bux-person">', 1)
            cards.append(c[:next_idx] if next_idx != -1 else c)

        for card in cards:
            link_m = PROFILE_LINK_RE.search(card)
            if not link_m:
                continue
            profile_path, name = link_m.groups()
            # OSU's own markup has at least one stray space in an href
            # (e.g. "/people/ brauner.14") - strip whitespace out of the path
            profile_path = re.sub(r"\s+", "", profile_path)
            name = html.unescape(re.sub(r"\s+", " ", name).strip())

            details_m = DETAILS_RE.search(card)
            title = html.unescape(re.sub(r"\s+", " ", details_m.group(1)).strip()) if details_m else ""

            email_m = EMAIL_RE.search(card)
            email = email_m.group(1).strip() if email_m else ""

            people.append({
                "name": name,
                "profile_url": BASE_URL + profile_path,
                "title": title,
                "email": email,
                "category": category,
            })
    return people


def parse_profile_bio(page_html):
    """Extract job title, email (fallback), and bio text from an individual
    profile page for medium classification. Restricted to the
    <article class="user-profile"> container - the full page also includes a
    sitewide "Areas of Study" nav menu that mentions every medium keyword on
    every page, which would otherwise swamp the classifier."""
    start = page_html.find('<article class="user-profile">')
    end = page_html.find("</article>", start) if start != -1 else -1
    article_html = page_html[start:end] if start != -1 and end != -1 else page_html

    text = re.sub(r"<script[^>]*>.*?</script>", "", article_html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    email_m = re.search(r"\b[\w.+-]+@osu\.edu\b", article_html)
    email = email_m.group(0) if email_m else ""

    return text, email


def main():
    parser = argparse.ArgumentParser(description="Scrape Ohio State Dept of Art faculty emails")
    parser.add_argument("--out", default="ohio_state_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0, help="seconds between profile fetches")
    args = parser.parse_args()

    dir_cache = os.path.join(CACHE_DIR, "people_directory.html")
    dir_html = fetch(DIRECTORY_URL, dir_cache, force_refresh=args.force_refresh)
    people = parse_directory(dir_html)
    print(f"Directory: {len(people)} people in scope (Chair/Faculty/Associated/Emeritus)")

    faculty = []
    skipped_no_medium = 0
    for i, person in enumerate(people, start=1):
        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch(person["profile_url"], profile_cache, force_refresh=args.force_refresh)
        bio_text, profile_email = parse_profile_bio(profile_html)

        email = person["email"] or profile_email
        email_type = "direct" if person["email"] else ("profile" if profile_email else "")

        medium = classify_medium(f"{person['title']} {bio_text}")
        if not medium:
            skipped_no_medium += 1
            continue
        if not email:
            continue

        faculty.append({
            "school_name": "Ohio State University, Department of Art",
            "faculty_name": person["name"],
            "title": person["title"],
            "department": person["category"],
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
    print(f"Skipped (no in-scope medium detected in title/bio): {skipped_no_medium}")


if __name__ == "__main__":
    main()
