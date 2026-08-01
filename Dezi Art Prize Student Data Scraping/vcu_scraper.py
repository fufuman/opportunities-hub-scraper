import argparse
import asyncio
import csv
import os
import re

URL = "https://icavcu.org/exhibitions/2025-mfa-thesis/"
CACHE_PATH = os.path.join("..", "cache", "vcu", "2025.html")

CREDIT_RE = re.compile(r"\(artwork © ([^;]+);")


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

    html = asyncio.run(fetch_via_crawl4ai(url))

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_students(html):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    credits = CREDIT_RE.findall(text_plain)

    seen = set()
    students = []
    for credit in credits:
        names = [n.strip() for n in credit.split(",") if n.strip()]
        collaborative = len(names) > 1
        for name in names:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            students.append({
                "name": name,
                "email": "",
                "major": "MFA Fine Arts",
                "graduation_year": "2025",
                "portfolio_url": "",
                "college": "VCU",
                "notes": "Name only, from artwork photo caption credit on ICA exhibition page"
                         + (" (collaborative piece, multiple credited artists)" if collaborative else "")
                         + "; likely incomplete relative to full graduating cohort",
            })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape VCU ICA 2025 MFA Thesis names from artwork credits")
    parser.add_argument("--out", default="vcu_students.csv")
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
