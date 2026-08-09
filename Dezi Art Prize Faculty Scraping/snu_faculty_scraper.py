import argparse
import asyncio
import csv
import html
import os
import re
from datetime import date

PAGES = [
    ("https://art.snu.ac.kr/en/category/design-en/?catemenu=Faculty&type=major", "Design"),
    ("https://art.snu.ac.kr/en/category/painting-en/?catemenu=Faculty&type=major", "Painting"),
    ("https://art.snu.ac.kr/en/category/sculpture-en/?catemenu=Faculty&type=major", "Sculpture"),
    ("https://art.snu.ac.kr/en/category/craft-en/?catemenu=Faculty&type=major", "Craft"),
    ("https://art.snu.ac.kr/en/category/oriental-painting-en/?catemenu=Faculty&type=major", "Oriental Painting"),
]

CACHE_DIR = os.path.join("..", "cache", "snu_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<div class="tadiv_col tadiv_body">)')
NAME_RE = re.compile(r'title="Permalink to ([^"]+)"', re.DOTALL)
POSITION_RE = re.compile(r'class="mposition">\s*([^<]*?)\s*</span>', re.DOTALL)
AREA_RE = re.compile(r'class="area hit">([^<]*)</span>', re.DOTALL)
EMAIL_RE = re.compile(r'title="send a e-mail">([^<]+)</a>', re.DOTALL)

MEDIUM_KEYWORDS = {
    "Painting/Drawing": ["painting", "drawing"],
    "Sculpture": ["sculpture", "ceramic", "metalwork", "jewelry", "jewellery"],
    "Filmmaking": ["film", "video", "moving image"],
    "Photography": ["photo"],
    "Design": ["spatial design", "product design", "graphic design", "living design",
               "visual communication", "industrial design", "branding"],
    "UI/UX Design": ["interaction", "ux design", "user interface", "digital environment"],
    "2D/3D Animation": ["animation", "motion design"],
    "Fashion": ["fashion", "textile design", "costume"],
    "Fiber and Material Arts": ["weav", "textile", "fiber", "craft", "printmaking", "print media"],
}
# department pages themselves are a reliable medium fallback signal when the
# area/position text alone doesn't contain a keyword (e.g. "Theory of Art")
DEPARTMENT_FALLBACK = {
    "Painting": "Painting/Drawing",
    "Sculpture": "Sculpture",
    "Craft": "Fiber and Material Arts",
    "Oriental Painting": "Painting/Drawing",
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


def classify_medium(area_text, department_label):
    haystack = area_text.lower()
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            return medium
    return DEPARTMENT_FALLBACK.get(department_label, "")


def parse_faculty(page_html, source_url, department_label):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="tadiv_col tadiv_body">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        position_m = POSITION_RE.search(card)
        area_m = AREA_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        position = html.unescape(re.sub(r"\s+", " ", position_m.group(1) if position_m else "").strip())
        area = html.unescape(re.sub(r"\s+", " ", area_m.group(1) if area_m else "").strip())
        email = email_m.group(1).strip()

        medium = classify_medium(f"{area} {position}", department_label)
        if not medium:
            continue

        faculty.append({
            "school_name": "Seoul National University, College of Fine Arts",
            "faculty_name": name,
            "title": position,
            "department": f"{department_label}" + (f" - {area}" if area else ""),
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape Seoul National University College of Fine Arts faculty emails")
    parser.add_argument("--out", default="snu_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for url, department_label in PAGES:
        slug = department_label.lower().replace(" ", "_")
        cache_path = os.path.join(CACHE_DIR, f"{slug}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url, department_label)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"{department_label}: {len(rows)} in-scope faculty ({len(new_rows)} new)")
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
