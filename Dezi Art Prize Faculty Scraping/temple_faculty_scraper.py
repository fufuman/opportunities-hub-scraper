import argparse
import asyncio
import csv
import html
import os
import re
from datetime import date

BASE_URL = "https://tyler.temple.edu/directory"
QUERY = "profile-type%5Bstaff%5D=staff&profile-type%5Bfaculty%5D=faculty&profile-type%5Badjunct_faculty%5D=adjunct_faculty"
NUM_PAGES = 10  # confirmed via pagination control on page 0 (2026-08-08)

CACHE_DIR = os.path.join("..", "cache", "temple_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<article class="teaser">)')
NAME_RE = re.compile(r"<h2>([^<]+)</h2>")
TITLE_RE = re.compile(r'professional-title">\s*([^<]*)</p>', re.DOTALL)
DISCIPLINE_RE = re.compile(r"<span>Discipline</span></strong><span>\s*([^<]*)</span>", re.DOTALL)
EMAIL_RE = re.compile(r'mailto:([^"]+)"')

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["paint", "draw"],
    "Sculpture": ["sculpt", "ceramic", "glass", "metal", "jewelry"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["graphic design", "visual communication", "industrial design", "art and design foundations"],
    "UI/UX Design": ["interaction design", "ui/ux", "ux design", "digital design"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "printmaking", "print media"],
}


async def fetch_via_crawl4ai(url):
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, wait_for="css:body", delay_before_return_html=3.0)
        if not result.success:
            raise RuntimeError(f"crawl4ai fetch failed: status={result.status_code}")
        return result.html


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    page_html = asyncio.run(fetch_via_crawl4ai(url))

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    return page_html


def classify_medium(discipline_text):
    haystack = discipline_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return ""


def parse_faculty(page_html, source_url):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<article class="teaser">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        title_m = TITLE_RE.search(card)
        discipline_m = DISCIPLINE_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1) if title_m else "").strip())
        discipline = html.unescape(re.sub(r"\s+", " ", discipline_m.group(1) if discipline_m else "").strip())
        email = email_m.group(1).strip()

        medium = classify_medium(discipline)
        if not medium:
            continue

        faculty.append({
            "school_name": "Temple University, Tyler School of Art and Architecture",
            "faculty_name": name,
            "title": title,
            "department": discipline,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape Temple/Tyler faculty directory emails")
    parser.add_argument("--out", default="temple_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for page in range(NUM_PAGES):
        url = f"{BASE_URL}?{QUERY}&page={page}"
        cache_path = os.path.join(CACHE_DIR, f"directory_page{page}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"page {page}: {len(rows)} in-scope faculty ({len(new_rows)} new)")
        all_faculty.extend(new_rows)

    fieldnames = ["school_name", "faculty_name", "title", "department", "medium",
                  "email", "email_type", "source_url", "date_extracted"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_faculty:
            writer.writerow(row)

    print(f"\nWrote {len(all_faculty)} faculty -> {args.out}")


if __name__ == "__main__":
    main()
