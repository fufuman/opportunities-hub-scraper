import argparse
import asyncio
import csv
import os
import re

THESIS_URL = "https://stamps.umich.edu/events/2025-mfa-thesis-exhibition"
GRAD_GALLERY_URL = "https://stamps.umich.edu/research-creative-work/graduate-work-mfa"
UNDERGRAD_GALLERY_URL = "https://stamps.umich.edu/research-creative-work/undergraduate-work"
CACHE_DIR = os.path.join("..", "cache", "umich")

H3_RE = re.compile(r"<h3>([^<]*)</h3>")

# "Stamps MFA 2026: Name" -> name, year
CLEAN_YEAR_PREFIX_RE = re.compile(r"^Stamps MFA (\d{4}):\s*(.+)$")
# "Name: 2024 MFA Profile" -> name, year
CLEAN_YEAR_SUFFIX_RE = re.compile(r"^(.+?):\s*(\d{4}) MFA Profile$")
# "Name: Profile" -> name, no year
CLEAN_NO_YEAR_RE = re.compile(r"^(.+?):\s*Profile$")
# Section header rows like "2025 MFA Thesis Exhibition" / "2024 Senior Exhibition" — skip these.
SECTION_HEADER_RE = re.compile(r"^\d{4}\s+(MFA Thesis Exhibition|Senior Exhibition|IP Exhibition)$")


async def fetch_via_crawl4ai(url):
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, wait_for="css:body", delay_before_return_html=6.0)
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


def parse_thesis_page(html):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    idx = text_plain.find("features the work of MFA students")
    if idx == -1:
        return []
    segment = text_plain[idx + len("features the work of MFA students"):]
    end = segment.find(".")
    names_blob = segment[:end] if end != -1 else segment
    names_blob = names_blob.replace(" and ", ", ")
    names = [n.strip() for n in names_blob.split(",") if n.strip()]

    return [{
        "name": name,
        "email": "",
        "major": "MFA",
        "graduation_year": "2025",
        "portfolio_url": THESIS_URL,
        "college": "U Michigan Stamps",
        "notes": "Name only, from thesis exhibition description text; "
                 "no email/portfolio published on source page",
    } for name in names]


def parse_gallery_page(html, source_url, major_label):
    titles = H3_RE.findall(html)
    students = []
    seen_clean_names = set()

    for title in titles:
        title = title.strip()
        if not title or SECTION_HEADER_RE.match(title):
            continue

        m = CLEAN_YEAR_PREFIX_RE.match(title)
        if m:
            year, name = m.group(1), m.group(2).strip()
            key = name.lower()
            if key in seen_clean_names:
                continue
            seen_clean_names.add(key)
            students.append({
                "name": name, "email": "", "major": major_label,
                "graduation_year": year, "portfolio_url": source_url,
                "college": "U Michigan Stamps",
                "notes": "From research/creative work gallery page",
            })
            continue

        m = CLEAN_YEAR_SUFFIX_RE.match(title)
        if m:
            name, year = m.group(1).strip(), m.group(2)
            key = name.lower()
            if key in seen_clean_names:
                continue
            seen_clean_names.add(key)
            students.append({
                "name": name, "email": "", "major": major_label,
                "graduation_year": year, "portfolio_url": source_url,
                "college": "U Michigan Stamps",
                "notes": "From research/creative work gallery page",
            })
            continue

        m = CLEAN_NO_YEAR_RE.match(title)
        if m:
            name = m.group(1).strip()
            key = name.lower()
            if key in seen_clean_names:
                continue
            seen_clean_names.add(key)
            students.append({
                "name": name, "email": "", "major": major_label,
                "graduation_year": "", "portfolio_url": source_url,
                "college": "U Michigan Stamps",
                "notes": "From research/creative work gallery page; "
                         "no graduation year listed for this entry",
            })
            continue

        # Ambiguous "Name: Artwork Title" (or possibly "Title: Name" reversed)
        # entries — no reliable year, and name-first order isn't guaranteed
        # (confirmed reversed on at least one real entry on this site).
        if ":" in title:
            name = title.split(":", 1)[0].strip()
            if name.lower() in seen_clean_names:
                continue
            students.append({
                "name": name, "email": "", "major": major_label,
                "graduation_year": "", "portfolio_url": source_url,
                "college": "U Michigan Stamps",
                "notes": "UNVERIFIED: from an artwork-title carousel entry ('Name: "
                         "Artwork Title' format) — no year available, name/title "
                         "order is not guaranteed (confirmed reversed on at least "
                         "one real entry on this site), and the same person may "
                         "appear multiple times for different artworks",
            })

    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape U Michigan Stamps MFA thesis + research/creative work galleries")
    parser.add_argument("--out", default="umich_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []

    thesis_html = fetch(THESIS_URL, os.path.join(CACHE_DIR, "2025-mfa-thesis.html"), args.force_refresh)
    thesis_students = parse_thesis_page(thesis_html)
    print(f"2025 MFA Thesis page: {len(thesis_students)} students")
    all_students.extend(thesis_students)

    grad_html = fetch(GRAD_GALLERY_URL, os.path.join(CACHE_DIR, "grad-gallery.html"), args.force_refresh)
    grad_students = parse_gallery_page(grad_html, GRAD_GALLERY_URL, "MFA (Graduate Research & Creative Work)")
    print(f"Graduate gallery: {len(grad_students)} entries")
    all_students.extend(grad_students)

    undergrad_html = fetch(UNDERGRAD_GALLERY_URL, os.path.join(CACHE_DIR, "undergrad-gallery.html"), args.force_refresh)
    undergrad_students = parse_gallery_page(undergrad_html, UNDERGRAD_GALLERY_URL, "BFA (Undergraduate Research & Creative Work)")
    print(f"Undergraduate gallery: {len(undergrad_students)} entries")
    all_students.extend(undergrad_students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    unverified = sum(1 for s in all_students if "UNVERIFIED" in s["notes"])
    print(f"\nWrote {len(all_students)} total entries -> {args.out}")
    print(f"Of which UNVERIFIED (ambiguous artwork-title entries): {unverified}")


if __name__ == "__main__":
    main()
