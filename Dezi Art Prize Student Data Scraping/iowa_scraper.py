import argparse
import csv
import html as html_module
import os
import re
import urllib.parse

URL = "https://art.uiowa.edu/events/mfa-virtual-exhibitions"
CACHE_PATH = os.path.join("..", "cache", "iowa", "mfa-virtual-exhibitions.html")

# One <p> per student: <a href="matterport-url"><strong>Name - MFA Exhibition
# (Discipline)</strong></a><br>Date Range</p>. A few entries have the name and
# discipline split across two adjacent <a> tags with slightly different
# Matterport URLs; take the first href found in either case.
ENTRY_RE = re.compile(
    r'<a href="([^"]*)"><strong>([^<]*?)</strong>\s*</a>'
    r'(?:<a href="[^"]*"><strong>([^<]*?)</strong>\s*</a>)?'
    r'<br>\s*([^<]*)</p>',
    re.DOTALL,
)
NAME_DISCIPLINE_RE = re.compile(r"^(.*?)\s*-\s*MFA Exhib[a-zA-Z]*ion\s*\(([^)]*)\)\s*$")


def unwrap_safelink(url):
    """Some links on this page are wrapped in Outlook Safelinks (email-link
    protection) rather than pointing straight at Matterport, apparently
    pasted in from a forwarded email. Unwrap to the real destination URL."""
    if "safelinks.protection.outlook.com" not in url:
        return url
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    real_url = qs.get("url", [None])[0]
    return real_url if real_url else url


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


def parse_students(html):
    start = html.find("Past exhibitions")
    segment = html[start:] if start != -1 else html

    students = []
    for href, part1, part2, date_range in ENTRY_RE.findall(segment):
        full_text = (part1 + (part2 or "")).strip()
        m = NAME_DISCIPLINE_RE.match(full_text)
        if not m:
            continue
        name = html_module.unescape(m.group(1).strip().rstrip(","))
        discipline = html_module.unescape(m.group(2).strip())

        # Prefer a plausible 4-digit year (20xx where xx is a real 2-digit
        # year, i.e. 2000-2099 with exactly 4 digits) — the source has at
        # least one typo ("20024" instead of "2024"), which would otherwise
        # match "2002" as the first 4 digits of a 5-digit run.
        year_matches = re.findall(r"\b(20\d{2})\d?\b", date_range)
        year = year_matches[-1] if year_matches else ""

        students.append({
            "name": name,
            "email": "",
            "major": f"MFA {discipline}",
            "graduation_year": year,
            "portfolio_url": unwrap_safelink(href.strip()),
            "college": "University of Iowa",
            "notes": "Portfolio URL is a Matterport 3D virtual exhibition tour, "
                     "not a personal site; no email published on source page",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape University of Iowa MFA Virtual Exhibitions page")
    parser.add_argument("--out", default="iowa_students.csv")
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

    from collections import Counter
    by_year = Counter(s["graduation_year"] for s in students)
    for year, count in sorted(by_year.items()):
        print(f"  {year}: {count}")


if __name__ == "__main__":
    main()
