import argparse
import asyncio
import csv
import os
import re

URL = "https://calarts.edu/high-pass"
CACHE_PATH = os.path.join("..", "cache", "calarts", "high-pass.html")


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

    html = asyncio.run(fetch_via_crawl4ai(url))

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_students(html):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    idx = text_plain.find("Exhibiting Artists include:")
    if idx == -1:
        return []
    segment = text_plain[idx + len("Exhibiting Artists include:"):]
    end = segment.find("Directory")
    names_blob = segment[:end] if end != -1 else segment

    names = [n.strip() for n in names_blob.split(",") if n.strip()]

    return [{
        "name": name,
        "email": "",
        "major": "BFA Art / Photo Media",
        "graduation_year": "2026",
        "portfolio_url": URL,
        "college": "CalArts",
        "notes": "Name only, from 'High Pass' BFA Class of 2026 group exhibition page; "
                 "no email/portfolio published on source page",
    } for name in names]


def main():
    parser = argparse.ArgumentParser(description="Scrape CalArts 'High Pass' BFA Class of 2026 exhibition")
    parser.add_argument("--out", default="calarts_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    html = fetch(URL, CACHE_PATH, force_refresh=args.force_refresh)
    students = parse_students(html)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)

    print(f"Wrote {len(students)} students -> {args.out}")


if __name__ == "__main__":
    main()
