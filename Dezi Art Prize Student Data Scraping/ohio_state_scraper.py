import argparse
import csv
import os
import re

CACHE_DIR = os.path.join("..", "cache", "osu")

# (url, cohort label, graduation year, whether names are cleanly comma-separated)
COHORTS = [
    ("https://art.osu.edu/events/mfa-thesis-exhibition-desire-lines", "2025", "2025", True),
    ("https://uas.osu.edu/events/waiting-light-change", "2026", "2026", False),
]


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


def extract_participating_artists_text(html):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    idx = text_plain.find("Participating Artists:")
    if idx == -1:
        return ""
    segment = text_plain[idx + len("Participating Artists:"):]
    end = segment.find("Reception:")
    if end == -1:
        end = segment.find("Filed in:")
    return segment[:end].strip() if end != -1 else segment[:500].strip()


def parse_clean_names(names_blob, year, source_url):
    names_blob = names_blob.replace("&nbsp;", " ")
    names = [n.strip() for n in names_blob.split(",") if n.strip()]
    students = []
    for name in names:
        students.append({
            "name": name,
            "email": "",
            "major": "MFA Studio Art",
            "graduation_year": year,
            "portfolio_url": source_url,
            "college": "Ohio State",
            "notes": "Name only, from 'Participating Artists' list; "
                     "no email/portfolio published on source page",
        })
    return students


def parse_ambiguous_names(names_blob, year, source_url):
    # This page's "Participating Artists" text mixes "Lastname, Firstname" and
    # "Firstname Lastname" with no reliable delimiter (e.g. "Banerjee, Shaheen
    # Beardsley, Maria Conlon, ..."). Best-effort reconstruction: pair the last
    # word of token[i] (a surname) with the first word of token[i+1] (the next
    # person's given name). Every row from this cohort is flagged as unverified
    # since this reconstruction cannot be confirmed against the source.
    tokens = [t.strip() for t in names_blob.split(",") if t.strip()]
    students = []
    for i in range(len(tokens) - 1):
        lastname = tokens[i].split()[-1]
        firstname = tokens[i + 1].split()[0]
        name = f"{firstname} {lastname}"
        students.append({
            "name": name,
            "email": "",
            "major": "MFA Studio Art",
            "graduation_year": year,
            "portfolio_url": source_url,
            "college": "Ohio State",
            "notes": "UNVERIFIED name reconstruction: source page lists names as "
                     "ambiguous run-on text mixing 'Lastname, Firstname' and "
                     "'Firstname Lastname' with no reliable delimiter; "
                     "double-check against the source page before using",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape Ohio State Department of Art MFA thesis exhibition rosters")
    parser.add_argument("--out", default="ohio_state_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for url, label, year, is_clean in COHORTS:
        cache_path = os.path.join(CACHE_DIR, f"{label}.html")
        html = fetch(url, cache_path, force_refresh=args.force_refresh)
        names_blob = extract_participating_artists_text(html)
        if is_clean:
            students = parse_clean_names(names_blob, year, url)
        else:
            students = parse_ambiguous_names(names_blob, year, url)
        print(f"{label}: {len(students)} students ({'clean' if is_clean else 'UNVERIFIED reconstruction'})")
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
