import argparse
import csv
import os
import re

URL = "https://www.cca.edu/newsroom/cca-presents-the-2026-mfa-fine-arts-graduate-exhibitions/"
CACHE_PATH = os.path.join("..", "cache", "cca", "mfa-2026-newsroom.html")


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
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    idx = text_plain.find("artists include")
    if idx == -1:
        return []
    segment = text_plain[idx + len("artists include"):]
    end = segment.find(".")
    names_blob = segment[:end] if end != -1 else segment

    names_blob = names_blob.replace(" and ", ", ")
    names = [n.strip() for n in names_blob.split(",") if n.strip()]

    students = []
    for name in names:
        students.append({
            "name": name,
            "email": "",
            "major": "MFA Fine Arts",
            "graduation_year": "2026",
            "portfolio_url": URL,
            "college": "CCA",
            "notes": "Name only, from CCA newsroom article text; "
                     "no email/portfolio published on source page",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape CCA 2026 MFA Fine Arts thesis exhibitors")
    parser.add_argument("--out", default="cca_students.csv")
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
