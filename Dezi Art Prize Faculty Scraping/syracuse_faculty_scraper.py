import argparse
import csv
import html
import os
import re
import time
from datetime import date

# The master directory (vpa.syracuse.edu/faculty-staff/) is a JS search widget
# with no default results, confirmed by the research brief and independently
# via WebFetch - not usable. This page has a Director + Administrative Staff
# with direct emails, plus 4 "Area Leads" (profile links + discipline label)
# whose emails require a profile click-through.
URL = "https://vpa.syracuse.edu/academics/art/contact/"
CACHE_DIR = os.path.join("..", "cache", "syracuse_faculty")

DIRECT_PERSON_RE = re.compile(
    r'<h2[^>]*><b>([^<]+)</b></h2><p[^>]*><a href="([^"]*)">([^<]+)</a>'
    r'.*?mailto:([^"]+)"',
    re.DOTALL,
)
AREA_LEAD_RE = re.compile(
    r'<a href="([^"]*faculty-staff[^"]*)">([^<]+)</a>,\s*([^<]+)</li>',
    re.DOTALL,
)
EMAIL_RE = re.compile(r'mailto:([^"]+)"', re.DOTALL)
BIO_RE = re.compile(r'class="biography-content">(.*?)</div>', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing", "illustration"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "printmaking", "print media"],
}
# "Studio Arts" alone (no specific medium named) can't be safely bucketed -
# leave unclassified rather than guess a medium
STUDIO_ARTS_GENERIC = "studio arts"


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
    if STUDIO_ARTS_GENERIC in haystack and not any(
        kw in haystack for kws in MEDIUM_KEYWORDS.values() for kw in kws
    ):
        return ""
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def main():
    parser = argparse.ArgumentParser(description="Scrape Syracuse VPA School of Art faculty emails")
    parser.add_argument("--out", default="syracuse_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    contact_cache = os.path.join(CACHE_DIR, "contact.html")
    contact_html = fetch(URL, contact_cache, force_refresh=args.force_refresh)

    faculty = []

    # Director (only direct-email person with a real teaching title; admin
    # staff excluded as non-faculty). No discipline is given on the contact
    # page for this role, so fall back to bio text on their own profile page
    # (same pattern as the area leads and as Ohio State/Cornell) rather than
    # leaving medium blank.
    director_m = re.search(
        r'School of Art Director</b></h2><p[^>]*><a href="([^"]*)">([^<]+)</a>.*?mailto:([^"]+)"',
        contact_html, re.DOTALL,
    )
    if director_m:
        profile_url, name, email = director_m.groups()
        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(profile_url)}.html")
        profile_html = fetch(profile_url, profile_cache, force_refresh=args.force_refresh)
        bio_m = BIO_RE.search(profile_html)
        medium = classify_medium(re.sub("<[^>]+>", " ", bio_m.group(1))) if bio_m else ""
        if medium:
            faculty.append({
                "school_name": "Syracuse University, College of Visual and Performing Arts, School of Art",
                "faculty_name": html.unescape(name.strip()),
                "title": "School of Art Director",
                "department": "School of Art",
                "medium": medium,
                "email": email.strip(),
                "email_type": "direct",
                "source_url": URL,
                "date_extracted": date.today().isoformat(),
            })

    # Area leads: discipline given directly on the contact page; email requires
    # visiting their profile page
    area_leads = AREA_LEAD_RE.findall(contact_html)
    for profile_url, name, discipline in area_leads:
        name = html.unescape(re.sub(r"\s+", " ", name).strip())
        discipline = html.unescape(re.sub(r"\s+", " ", discipline).strip())

        medium = classify_medium(discipline)
        if not medium:
            continue

        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(profile_url)}.html")
        profile_html = fetch(profile_url, profile_cache, force_refresh=args.force_refresh)
        email_m = EMAIL_RE.search(profile_html)
        if not email_m:
            continue
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Syracuse University, College of Visual and Performing Arts, School of Art",
            "faculty_name": name,
            "title": f"Area Lead, {discipline}",
            "department": discipline,
            "medium": medium,
            "email": email,
            "email_type": "profile",
            "source_url": profile_url,
            "date_extracted": date.today().isoformat(),
        })
        print(f"  {name}: {medium} ({email})")

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
