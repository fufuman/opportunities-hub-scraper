import argparse
import csv
import os
import re

CACHE_DIR = os.path.join("..", "cache", "mcad")

# Each cohort: url, graduation year, and which HTML entry format it uses.
COHORTS = [
    {
        "year": "2022",
        "url": "https://www.mcad.edu/events/spring-2022-commencement",
        "format": "namecard",
    },
    {
        "year": "2023",
        "url": "https://www.mcad.edu/events/spring-2023-commencement-ceremony",
        "format": "flat",
    },
]

DEGREE_HEADING_RE = re.compile(r'<h2 class="text-align-center">([^<]+)</h2>')

# 2022 format: <span class="NameCard"><strong>Name, </strong>Major<br>Hometown<br>
#   [<a href="website">...</a><br>][<a href="mailto:...">...</a>]</span>
NAMECARD_ENTRY_RE = re.compile(
    r'<span class="NameCard"><strong>(?P<name>[^<]*?),\s*</strong>'
    r'(?P<major>[^<]*?)<br>\s*'
    r'(?P<hometown>[^<]*?)(?:<br>\s*)?'
    r'(?:<a href="(?P<website>[^"]*)"[^>]*>[^<]*</a><br>\s*)?'
    r'(?:<a href="mailto:(?P<email>[^"]*)">[^<]*</a>)?'
    r'</span>',
    re.DOTALL,
)

# 2023 format: <p class="text-align-center"><span><strong>Name,</strong> Major<br>
#   Hometown[<br>links]</span>[<br>links]</p>
# Handles quirks in the source: entries with no <br> at all (major/hometown run
# together), and entries with links inside the </span> instead of after it.
FLAT_ENTRY_RE = re.compile(
    r'<p class="text-align-center"><span><strong>(?P<name>[^<]*?),</strong>\s*'
    r'(?P<rest>.*?)</span>'
    r'(?:<br>\s*(?P<links_after>.*?))?'
    r'</p>',
    re.DOTALL,
)
LINK_RE = re.compile(r'<a href="(?P<href>[^"]*)"[^>]*>([^<]*)</a>')


def fetch_html(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_namecard_format(html, year):
    parts = DEGREE_HEADING_RE.split(html)
    students = []
    for i in range(1, len(parts), 2):
        degree = parts[i].strip()
        segment = parts[i + 1] if i + 1 < len(parts) else ""
        for m in NAMECARD_ENTRY_RE.finditer(segment):
            name = (m.group("name") or "").strip()
            major = (m.group("major") or "").strip()
            hometown = (m.group("hometown") or "").strip()
            website = (m.group("website") or "").strip()
            email = (m.group("email") or "").strip()

            students.append({
                "name": name,
                "email": email,
                "major": major,
                "graduation_year": year,
                "portfolio_url": website,
                "college": "MCAD",
                "notes": f"Degree: {degree}; Hometown: {hometown}" if hometown else f"Degree: {degree}",
            })
    return students


def parse_flat_format(html, year):
    start = html.find("Graduating Students</h2>")
    end = html.find("Land Acknowledgement", start) if start != -1 else -1
    segment = html[start:end] if start != -1 and end != -1 else html

    students = []
    for m in FLAT_ENTRY_RE.finditer(segment):
        name = (m.group("name") or "").strip()
        rest = m.group("rest") or ""
        links_after = m.group("links_after") or ""

        # Any <a> tags may live inside `rest` (some entries) or in `links_after`
        # (most entries) — pull links out of both, then treat whatever plain
        # text remains in `rest` (split on <br>) as major/hometown lines.
        website = ""
        email = ""
        for href, _text in LINK_RE.findall(rest) + LINK_RE.findall(links_after):
            href = href.strip()
            if href.lower().startswith("mailto:"):
                email = href[len("mailto:"):].strip()
            elif href:
                website = href

        text_only = LINK_RE.sub("", rest)
        text_only = re.sub(r"\s*\|\s*$", "", text_only).strip()
        lines = [ln.strip() for ln in re.split(r"<br\s*/?>", text_only) if ln.strip()]

        major = lines[0] if len(lines) >= 1 else ""
        hometown = lines[1] if len(lines) >= 2 else ""

        students.append({
            "name": name,
            "email": email,
            "major": major,
            "graduation_year": year,
            "portfolio_url": website,
            "college": "MCAD",
            "notes": f"Hometown: {hometown}" if hometown else "",
        })
    return students


def parse_students(html, year, fmt):
    if fmt == "namecard":
        return parse_namecard_format(html, year)
    if fmt == "flat":
        return parse_flat_format(html, year)
    raise ValueError(f"Unknown format: {fmt}")


def main():
    parser = argparse.ArgumentParser(description="Scrape MCAD commencement rosters across cohorts")
    parser.add_argument("--out", default="mcad_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for cohort in COHORTS:
        cache_path = os.path.join(CACHE_DIR, f"mcad_{cohort['year']}_raw.html")
        html = fetch_html(cohort["url"], cache_path, force_refresh=args.force_refresh)
        students = parse_students(html, cohort["year"], cohort["format"])
        missing_email = sum(1 for s in students if not s["email"])
        missing_website = sum(1 for s in students if not s["portfolio_url"])
        print(f"{cohort['year']}: {len(students)} students "
              f"(missing email: {missing_email}, missing website: {missing_website})")
        all_students.extend(students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    print(f"\nWrote {len(all_students)} total students -> {args.out}")


if __name__ == "__main__":
    main()
