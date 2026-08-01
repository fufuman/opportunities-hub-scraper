import argparse
import csv
import io
import os
import re
import sys
from datetime import datetime

DEFAULT_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1IntZSBI3HdedUVGH8rISCp36D9a_WSYGWNTFjBpud38/export?format=csv&gid=1215246886"
)
DEFAULT_CACHE_PATH = os.path.join("..", "cache", "rit_sheet.csv")

PROGRAM_RE = re.compile(r"^(.*?)\s*\(([^()]+)\)\s*$")
YEAR_RE = re.compile(r"(20\d{2})")


def fetch_sheet_csv(csv_url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8", newline="") as f:
            return f.read()

    import urllib.request

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/csv,*/*;q=0.8",
    }
    req = urllib.request.Request(csv_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        raw_text = resp.read().decode("utf-8-sig", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8", newline="") as f:
        f.write(raw_text)

    return raw_text


def derive_major(program_raw):
    program_raw = (program_raw or "").strip()
    if not program_raw:
        return ""
    m = PROGRAM_RE.match(program_raw)
    if m:
        return m.group(1).strip()
    return program_raw


def derive_graduation_year(expected_grad_raw):
    s = (expected_grad_raw or "").strip()
    if not s:
        return ""
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return str(datetime.strptime(s, fmt).year)
        except ValueError:
            continue
    m = YEAR_RE.search(s)
    if m:
        return m.group(1)
    return ""


def parse_students(raw_csv_text):
    reader = csv.DictReader(io.StringIO(raw_csv_text))
    students = []
    skipped_blank = 0

    for row in reader:
        if not any((v or "").strip() for v in row.values()):
            skipped_blank += 1
            continue

        first_name = (row.get("First Name") or "").strip()
        last_name = (row.get("Last Name") or "").strip()
        name = f"{first_name} {last_name}".strip()

        email = (row.get("Email") or "").strip()
        if not email:
            email = (row.get("Email Address") or "").strip()

        major = derive_major(row.get("Program"))
        graduation_year = derive_graduation_year(row.get("Expected Graduation"))
        portfolio_url = (row.get("Portfolio URL") or "").strip()

        students.append({
            "name": name,
            "email": email,
            "major": major,
            "graduation_year": graduation_year,
            "portfolio_url": portfolio_url,
        })

    if skipped_blank:
        print(f"Skipped {skipped_blank} blank row(s) in source CSV.", file=sys.stderr)

    return students


def write_csv(students, out_path):
    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            writer.writerow(s)


def report_counts(students):
    print(f"Total students: {len(students)}")
    counts = {}
    for s in students:
        key = s["major"] or "(unspecified)"
        counts[key] = counts.get(key, 0) + 1

    missing_email = sum(1 for s in students if not s["email"])
    missing_grad_year = sum(1 for s in students if not s["graduation_year"])

    print("\nBy major:")
    for major, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {major}: {count}")

    print(f"\nMissing email: {missing_email}")
    print(f"Missing graduation_year: {missing_grad_year}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract RIT College of Art and Design student names/emails "
        "from the public Google Sheet backing creativity.cad.rit.edu"
    )
    parser.add_argument("--out", default="rit_students.csv", help="Output CSV path")
    parser.add_argument("--sheet-url", default=DEFAULT_SHEET_URL, help="Google Sheet CSV export URL")
    parser.add_argument("--cache-path", default=DEFAULT_CACHE_PATH, help="Local cache path for raw CSV")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass cache and re-fetch the sheet")
    args = parser.parse_args()

    raw_csv_text = fetch_sheet_csv(args.sheet_url, args.cache_path, force_refresh=args.force_refresh)
    students = parse_students(raw_csv_text)
    write_csv(students, args.out)

    print(f"Wrote {len(students)} students -> {args.out}\n")
    report_counts(students)


if __name__ == "__main__":
    main()
