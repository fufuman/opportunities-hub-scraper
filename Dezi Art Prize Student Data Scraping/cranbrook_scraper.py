import argparse
import csv
import json
import os
import re

BASE_URL = "https://cranbrookart.edu/alumni/directory/"
ENV_SCRIPT_RE = re.compile(
    r'<script type="application/json" id="bbg-common-env">(.*?)</script>',
    re.DOTALL,
)


def fetch_year_html(year, cache_dir, force_refresh=False):
    cache_path = os.path.join(cache_dir, f"cranbrook_{year}.html")
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request
    import urllib.parse

    url = f"{BASE_URL}?{urllib.parse.urlencode({'y': year})}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_students(html, year):
    m = ENV_SCRIPT_RE.search(html)
    if not m:
        raise RuntimeError(f"Could not find embedded alumni JSON for year {year}")

    data = json.loads(m.group(1))
    posts = data.get("posts") or []

    students = []
    for p in posts:
        first = (p.get("firstname") or "").strip()
        last = (p.get("lastname") or "").strip()
        name = f"{first} {last}".strip()
        email = (p.get("email") or "").strip() or "Not found"
        website = (p.get("url") or "").strip() or (p.get("post_url") or "").strip()

        students.append({
            "name": name,
            "email": email,
            "major": (p.get("department") or "").strip(),
            "graduation_year": str(p.get("year") or year),
            "portfolio_url": website,
            "college": "Cranbrook",
            "notes": "Email not published in alumni directory" if email == "Not found" else "",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Cranbrook Academy of Art alumni directory by year")
    parser.add_argument("--years", nargs="+", type=int, default=[2025, 2026])
    parser.add_argument("--out", default="cranbrook_students.csv")
    parser.add_argument("--cache-dir", default=os.path.join("..", "cache", "cranbrook"))
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for year in args.years:
        html = fetch_year_html(year, args.cache_dir, force_refresh=args.force_refresh)
        students = parse_students(html, year)
        print(f"Year {year}: {len(students)} students")
        all_students.extend(students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    print(f"\nWrote {len(all_students)} students -> {args.out}")


if __name__ == "__main__":
    main()
