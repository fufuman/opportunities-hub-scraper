import argparse
import asyncio
import csv
import html
import os
import re
from datetime import date

# Department-specific "Faculty Members" pages auto-load that department's own
# roster by default (found via crawl4ai render - the plain-fetched HTML shows
# only an empty search widget, no static data). University-wide search
# (/Faculty-Dashboard/All-Faculty) and the FFA-level staff search page were
# both JS-driven with no default results, unlike these department pages.
PAGES = [
    ("https://jmi.ac.in/ACADEMICS/Departments/Department-Of-Painting/Faculty-Members", "Painting", "Painting/Drawing"),
    ("https://jmi.ac.in/ACADEMICS/Departments/Department-Of-Sculpture/Faculty-Members", "Sculpture", "Sculpture"),
    ("https://jmi.ac.in/ACADEMICS/Departments/Department-Of-Applied-Art/Faculty-Members", "Applied Art", "Design"),
]

CACHE_DIR = os.path.join("..", "cache", "jamia_faculty")

CARD_SPLIT_RE = re.compile(r'(?=<div class="team-item">)')
NAME_RE = re.compile(r'person-name[^>]*>\s*<a[^>]*>([^<]+)</a>', re.DOTALL)
DESIGNATION_RE = re.compile(r'class="designation[^"]*">([^<]*)</span>', re.DOTALL)
EMAIL_RE = re.compile(r"mailto:'?([\w.+-]+@[\w.-]+\.\w+)'?\"", re.DOTALL)


async def fetch_via_crawl4ai(url):
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, wait_for="css:body", delay_before_return_html=5.0)
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


def parse_faculty(page_html, source_url, department_label, medium):
    faculty = []
    raw_cards = CARD_SPLIT_RE.split(page_html)[1:]
    cards = []
    for c in raw_cards:
        next_idx = c.find('<div class="team-item">', 1)
        cards.append(c[:next_idx] if next_idx != -1 else c)

    for card in cards:
        name_m = NAME_RE.search(card)
        email_m = EMAIL_RE.search(card)
        if not name_m or not email_m:
            continue
        desig_m = DESIGNATION_RE.search(card)

        name = html.unescape(re.sub(r"\s+", " ", name_m.group(1)).strip())
        designation = html.unescape(re.sub(r"\s+", " ", desig_m.group(1) if desig_m else "").strip())
        email = email_m.group(1).strip()

        faculty.append({
            "school_name": "Jamia Millia Islamia, Faculty of Fine Arts",
            "faculty_name": name,
            "title": designation,
            "department": department_label,
            "medium": medium,
            "email": email,
            "email_type": "direct",
            "source_url": source_url,
            "date_extracted": date.today().isoformat(),
        })
    return faculty


def main():
    parser = argparse.ArgumentParser(description="Scrape Jamia Millia Islamia Faculty of Fine Arts faculty emails")
    parser.add_argument("--out", default="jamia_faculty.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_faculty = []
    seen_emails = set()
    for url, department_label, medium in PAGES:
        slug = department_label.lower().replace(" ", "_")
        cache_path = os.path.join(CACHE_DIR, f"{slug}.html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        rows = parse_faculty(page_html, url, department_label, medium)
        new_rows = [r for r in rows if r["email"].lower() not in seen_emails]
        for r in new_rows:
            seen_emails.add(r["email"].lower())
        print(f"{department_label}: {len(rows)} faculty ({len(new_rows)} new)")
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
