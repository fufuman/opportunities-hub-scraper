import argparse
import csv
import html as html_module
import os
import re

CACHE_DIR = os.path.join("..", "cache", "mica")
HUB_URL = "https://www.mica.edu/gradshow"
BASE_URL = "https://www.mica.edu/events-exhibitions/annual-events-series/commencement/grad-show-2026/"

PROGRAM_SLUGS = [
    "community-arts-mfa",
    "curatorial-studies-mfa",
    "filmmaking-mfa",
    "graphic-design-ma",
    "graphic-design-mfa",
    "illustration-ma",
    "illustration-practice-mfa",
    "leroy-e-hoffberger-school-of-painting-mfa",
    "mount-royal-school-of-art-mfa",
    "photography-media-society-mfa",
    "rinehart-school-of-sculpture-mfa",
    "social-design-ma",
    "studio-art-mfa-summer-low-residency",
    "teaching-ma",
]

PROGRAM_LABELS = {
    "community-arts-mfa": "Community Arts MFA",
    "curatorial-studies-mfa": "Curatorial Studies MFA",
    "filmmaking-mfa": "Filmmaking MFA",
    "graphic-design-ma": "Graphic Design MA",
    "graphic-design-mfa": "Graphic Design MFA",
    "illustration-ma": "Illustration MA",
    "illustration-practice-mfa": "Illustration Practice MFA",
    "leroy-e-hoffberger-school-of-painting-mfa": "Painting MFA (Leroy E. Hoffberger School)",
    "mount-royal-school-of-art-mfa": "Mount Royal School of Art MFA",
    "photography-media-society-mfa": "Photography & Media & Society MFA",
    "rinehart-school-of-sculpture-mfa": "Sculpture MFA (Rinehart School)",
    "social-design-ma": "Social Design MA",
    "studio-art-mfa-summer-low-residency": "Studio Art MFA (Summer Low-Residency)",
    "teaching-ma": "Teaching MA",
}

# Heading wording varies by program page: "Participating students" or just
# "Participating" (with a trailing &nbsp;).
HEADING_RE = re.compile(r"Participating(?:\s+students)?(?:&nbsp;)?\s*</h2>\s*<ul>")
LINK_RE = re.compile(r'<a href="([^"]*)"[^>]*>([^<]*)</a>')
NAME_RE = re.compile(r"<strong>([^<]*)</strong>")


def find_top_level_items(html, start_pos):
    """Walk the <ul> starting at start_pos and yield each top-level <li>'s
    inner HTML, correctly skipping over any nested <ul>...</ul> (e.g. MICA's
    Curatorial Studies page nests exhibition-detail sub-lists inside a
    student's <li>, which would otherwise close a naive regex match early).
    start_pos is just after the opening <ul> tag itself, so depth starts at 1."""
    depth = 1
    i = start_pos
    item_start = None
    items = []
    tag_re = re.compile(r"<(/?)(ul|li)\b[^>]*>")
    while i < len(html):
        m = tag_re.search(html, i)
        if not m:
            break
        closing, tag = m.group(1), m.group(2)
        if tag == "ul":
            depth += 1 if not closing else -1
            if depth == 0:
                break
        elif tag == "li" and depth == 1:
            if not closing:
                item_start = m.end()
            else:
                if item_start is not None:
                    items.append(html[item_start:m.start()])
                item_start = None
        i = m.end()
    return items


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_program_page(html, program_label, source_url):
    m = HEADING_RE.search(html)
    if not m:
        return []

    li_items = find_top_level_items(html, m.end())

    students = []
    for li_html in li_items:
        # A name is usually one <strong> tag, but is sometimes split across
        # two (e.g. "<strong>Taro</strong> <strong>Cantú</strong>") — join all
        # <strong> fragments in this <li> to reconstruct the full name.
        name_parts = NAME_RE.findall(li_html)
        if not name_parts:
            continue
        name = " ".join(html_module.unescape(p).strip() for p in name_parts)
        name = re.sub(r"\s+", " ", name).strip()
        if not name:
            continue

        portfolio_url = ""
        for href, label in LINK_RE.findall(li_html):
            label_clean = label.strip().lower()
            if label_clean == "website":
                portfolio_url = href
                break
        if not portfolio_url:
            for href, label in LINK_RE.findall(li_html):
                if "instagram.com" in href:
                    portfolio_url = href
                    break

        students.append({
            "name": name,
            "email": "",
            "major": program_label,
            "graduation_year": "2026",
            "portfolio_url": portfolio_url or source_url,
            "college": "MICA",
            "notes": "" if portfolio_url else "No website/Instagram link listed for this student",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape MICA Grad Show 2026 participating students by program")
    parser.add_argument("--out", default="mica_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for slug in PROGRAM_SLUGS:
        url = BASE_URL + slug + "/"
        cache_path = os.path.join(CACHE_DIR, f"{slug}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)
        label = PROGRAM_LABELS[slug]
        students = parse_program_page(html, label, url)
        print(f"{slug}: {len(students)} students")
        all_students.extend(students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    missing_link = sum(1 for s in all_students if "No website/Instagram" in s["notes"])
    print(f"\nWrote {len(all_students)} students -> {args.out}")
    print(f"Missing website/Instagram link: {missing_link}")


if __name__ == "__main__":
    main()
