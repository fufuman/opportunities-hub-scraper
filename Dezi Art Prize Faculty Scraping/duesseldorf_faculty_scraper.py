import argparse
import asyncio
import csv
import html
import os
import re
import time
from datetime import date

# The brief classified this as Tier 3 (no emails, use postmaster@ general
# contact). Checked one profile page directly - the listing page shows only
# "javascript:;" where an email would be (client-side obfuscation), but the
# fully-rendered page (crawl4ai) resolves a real institutional email in the
# page's own meta description text. Only the "Freie Kunst" (Free Art) section
# is in scope - Baukunst (Architecture) and Kunstbezogene Wissenschaften
# (Art-related theory/sciences) are excluded per user's medium list. Each
# "Freie Kunst" professor runs their own individually-named class (e.g.
# "Klasse Bircken") covering whatever medium they personally work in, with no
# separate discipline field on the listing - medium must be read from each
# person's own bio/description text, found only after full JS rendering.
URL = "https://kunstakademie-duesseldorf.de/studienangebot-und-bewerbung/professor-innen/"
CACHE_DIR = os.path.join("..", "cache", "duesseldorf_faculty")

# Section boundaries found by reading the page's heading sequence in document
# order (2026-08-09) - "Freie Kunst" starts after the main title, ends at
# "Baukunst". Hardcoded from that one-time read since there's no structural
# marker separating sections other than heading text order.
FREIE_KUNST_NAMES_STOP_AT = "Sara Deraedt"  # last Freie Kunst entry before "Baukunst" heading

PROFILE_LINK_RE = re.compile(r'<a href="(https://kunstakademie-duesseldorf\.de/studienangebot-und-bewerbung/professor-innen/[a-z0-9-]+/)">([^<]+)</a>')
EMAIL_RE = re.compile(r"([\w.+-]+@kunstakademie-duesseldorf\.de)")

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["malerei", "zeichnung", "painting", "drawing"],
    "Sculpture": ["bildhauerei", "skulptur", "keramik", "sculpture", "ceramic"],
    "Filmmaking": ["film", "video", "bewegtbild"],
    "Photography": ["fotografie", "photo"],
    "Design": ["design", "grafik"],
    "UI/UX Design": ["interaktion", "digital"],
    "2D/3D Animation": ["animation"],
    "Fashion": ["mode", "fashion", "textil"],
    "Fiber and Material Arts": ["textile", "weberei", "material"],
}


async def fetch_via_crawl4ai(url):
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, wait_for="css:body", delay_before_return_html=3.0)
        if not result.success:
            raise RuntimeError(f"crawl4ai fetch failed: status={result.status_code}")
        return result.html


def fetch_plain(url, cache_path, force_refresh=False):
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


def fetch_rendered(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    page_html = asyncio.run(fetch_via_crawl4ai(url))

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


def main():
    parser = argparse.ArgumentParser(description="Scrape Kunstakademie Dusseldorf Freie Kunst professor emails")
    parser.add_argument("--out", default="duesseldorf_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    listing_cache = os.path.join(CACHE_DIR, "professors.html")
    listing_html = fetch_plain(URL, listing_cache, force_refresh=args.force_refresh)

    people = []
    seen = set()
    for profile_url, name in PROFILE_LINK_RE.findall(listing_html):
        if profile_url in seen:
            continue
        seen.add(profile_url)
        name = html.unescape(name.strip())
        people.append({"profile_url": profile_url, "name": name})
        if FREIE_KUNST_NAMES_STOP_AT in name:
            break

    print(f"Freie Kunst section: {len(people)} professors")

    faculty = []
    for i, person in enumerate(people, start=1):
        profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
        profile_html = fetch_rendered(person["profile_url"], profile_cache, force_refresh=args.force_refresh)

        email_m = EMAIL_RE.search(profile_html)
        medium = classify_medium(profile_html)
        if not email_m or not medium:
            if not os.path.exists(profile_cache) or args.force_refresh:
                time.sleep(args.sleep)
            continue
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Kunstakademie Dusseldorf (Dusseldorf Art Academy)",
            "faculty_name": person["name"],
            "title": "Professor, Freie Kunst",
            "department": "Freie Kunst",
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
