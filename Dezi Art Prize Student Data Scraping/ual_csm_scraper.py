"""
UAL Central Saint Martins Graduate Showcase scraper.

The listing page (ualshowcase.arts.ac.uk/c/central-saint-martins?...) is a
JS-rendered, scroll-triggered grid - a plain fetch or a passively-rendered
crawl4ai fetch just shows "Loading projects" forever. Requires a real
Playwright page with an active mouse-wheel scroll to trigger the lazy load.

Each of the 12 project cards per page links out via a search-redirect URL
wrapping the real profile URL (e.g. ualshowcase.arts.ac.uk/@shreyaagrawal) in
a url= query param. Profile pages publish a real mailto: link directly in the
DOM (no interaction needed despite the icon only being visually revealed on
hover in a browser).

Pagination: num_ranks=12 per page, start_rank is 1-indexed and increments by
12 (page N starts at rank (N-1)*12 + 1). Page 17 = start_rank 193.
"""
import argparse
import asyncio
import csv
import os
import re
import time
from datetime import date
from urllib.parse import unquote

BASE_LISTING_URL = (
    "https://ualshowcase.arts.ac.uk/c/central-saint-martins"
    "?query=%21nullquery&collection=ual%7Esp-showcase&num_ranks=12"
    "&sort=dmetasortKey&meta_hideFromCollege_sand=0"
    "&meta_college_sand=Central+Saint+Martins&start_rank={start_rank}"
)
NUM_RANKS = 12
CACHE_DIR = os.path.join("..", "cache", "ual_csm")

COURSE_RE = re.compile(
    r'project-card-course-name">\s*<p[^>]*>Course</p>\s*<a[^>]*>([^<]+)</a>',
    re.DOTALL,
)
REDIRECT_LINK_RE = re.compile(r'href="(https://ual-search\.arts\.ac\.uk/s/redirect\?[^"]+)"')
URL_PARAM_RE = re.compile(r"[?&](?:amp;)?url=([^&\";]+)")
PROJECT_NAME_RE = re.compile(r'project-title">([^<]*)</p>')
STUDENT_NAME_RE = re.compile(r'heading" aria-labelledby="project-dataset-title">([^<]+)</h3>')
EMAIL_RE = re.compile(r'mailto:([^"]+)"')

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing", "illustration"],
    "Sculpture": ["sculpture", "ceramic", "jewellery", "jewelry", "glass", "metalwork"],
    "Filmmaking": ["film", "moving image", "animation film"],
    "Photography": ["photograph"],
    "Design": ["graphic communication design", "graphic design", "visual communication"],
    "UI/UX Design": ["interaction design", "user experience", "ui/ux", "digital design"],
    "2D/3D Animation": ["animation"],
    "Fashion": ["fashion"],
    "Fiber and Material Arts": ["textile", "weav", "fiber", "fibre", "material practice"],
}
# Excluded per user decision 2026-08-15: Industrial Design (too far from our
# Design scope), Culture/Criticism/Curation (curatorial studies, not a medium),
# Architecture (never in scope), and anything not matching a keyword above.
FINE_ART_RE = re.compile(r"\bfine art\b", re.IGNORECASE)


def classify_medium(course_text):
    haystack = course_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    if FINE_ART_RE.search(course_text):
        return "Painting/Drawing"
    return ""


async def fetch_listing_page(page, start_rank, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    url = BASE_LISTING_URL.format(start_rank=start_rank)
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)
    for _ in range(5):
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1200)

    html = await page.content()
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def parse_listing(html):
    """Return list of dicts: project_title, student_name, course, profile_url."""
    # split on each project card boundary
    cards = re.split(r'(?=<li class="sc-1cb21671-3)', html)[1:]
    people = []
    for card in cards:
        redirect_m = REDIRECT_LINK_RE.search(card)
        course_m = COURSE_RE.search(card)
        project_m = PROJECT_NAME_RE.search(card)
        student_m = STUDENT_NAME_RE.search(card)
        if not redirect_m or not student_m:
            continue

        url_param_m = URL_PARAM_RE.search(redirect_m.group(1))
        if not url_param_m:
            continue
        profile_url = unquote(url_param_m.group(1))

        people.append({
            "profile_url": profile_url,
            "student_name": student_m.group(1).strip(),
            "project_title": project_m.group(1).strip() if project_m else "",
            "course": course_m.group(1).strip() if course_m else "",
        })
    return people


async def fetch_profile_email(page, profile_url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        await page.goto(profile_url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(1500)
        html = await page.content()
        os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)

    email_m = EMAIL_RE.search(html)
    return email_m.group(1).strip() if email_m else ""


def slugify(url):
    return re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")


async def run(start_page, end_page, out_path, force_refresh, sleep_s):
    from playwright.async_api import async_playwright

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url",
                  "college", "notes", "sent_to_nitya"]

    existing_rows = []
    if os.path.exists(out_path):
        with open(out_path, "r", newline="", encoding="utf-8") as f:
            existing_rows = list(csv.DictReader(f))
    seen_names = {r["name"] for r in existing_rows}

    new_rows = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        for page_num in range(start_page, end_page + 1):
            start_rank = (page_num - 1) * NUM_RANKS + 1
            listing_cache = os.path.join(CACHE_DIR, f"listing_page{page_num}.html")
            html = await fetch_listing_page(page, start_rank, listing_cache, force_refresh)
            people = parse_listing(html)
            print(f"page {page_num} (start_rank={start_rank}): {len(people)} projects found")

            for person in people:
                medium = classify_medium(person["course"])
                if not medium:
                    continue
                if person["student_name"] in seen_names:
                    continue

                profile_cache = os.path.join(CACHE_DIR, "profiles", f"{slugify(person['profile_url'])}.html")
                email = await fetch_profile_email(page, person["profile_url"], profile_cache, force_refresh)
                if not email:
                    continue

                seen_names.add(person["student_name"])
                new_rows.append({
                    "name": person["student_name"],
                    "email": email,
                    "major": person["course"],
                    "graduation_year": "",
                    "portfolio_url": person["profile_url"],
                    "college": "UAL Central Saint Martins",
                    "notes": f"Medium: {medium}; project '{person['project_title']}'; "
                             f"email found via mailto: link on UAL Showcase profile page",
                    "sent_to_nitya": "",
                })
                print(f"  + {person['student_name']} ({medium}): {email}")

                if not os.path.exists(profile_cache) or force_refresh:
                    time.sleep(sleep_s)

        await browser.close()

    all_rows = existing_rows + new_rows
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"\nAdded {len(new_rows)} new students with email (pages {start_page}-{end_page})")
    print(f"Total in {out_path}: {len(all_rows)}")


def main():
    parser = argparse.ArgumentParser(description="Scrape UAL Central Saint Martins graduate showcase")
    parser.add_argument("--start-page", type=int, required=True)
    parser.add_argument("--end-page", type=int, required=True)
    parser.add_argument("--out", default="ual_csm_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    asyncio.run(run(args.start_page, args.end_page, args.out, args.force_refresh, args.sleep))


if __name__ == "__main__":
    main()
