import argparse
import csv
import html as html_module
import os
import re

CACHE_DIR = os.path.join("..", "cache", "calarts_animation")

PAGES = [
    ("character-animation/bfa-1", "Character Animation", "BFA 1"),
    ("character-animation/bfa-2", "Character Animation", "BFA 2"),
    ("character-animation/bfa-3", "Character Animation", "BFA 3"),
    ("character-animation/bfa-4", "Character Animation", "BFA 4"),
    ("character-animation/affiliates", "Character Animation", "Affiliates"),
    ("character-animation/recent-alumni", "Character Animation", "Recent Alumni"),
    ("experimental-animation/bfa-1", "Experimental Animation", "BFA 1"),
    ("experimental-animation/bfa-2", "Experimental Animation", "BFA 2"),
    ("experimental-animation/bfa-3", "Experimental Animation", "BFA 3"),
    ("experimental-animation/bfa-4", "Experimental Animation", "BFA 4"),
    ("experimental-animation/mfa-1", "Experimental Animation", "MFA 1"),
    ("experimental-animation/mfa-2", "Experimental Animation", "MFA 2"),
    ("experimental-animation/mfa-3", "Experimental Animation", "MFA 3"),
    ("experimental-animation/recent-alumni", "Experimental Animation", "Recent Alumni"),
]
BASE_URL = "https://calarts.edu/filmvideo/animation-student-portfolios/2026/"

NAME_RE = re.compile(
    r'<h2 class="text-theme-heading-color[^"]*">([^<]+)</h2>\s*'
    r'<p class="text-sm[^"]*">([^<]*)</p>\s*'
    r'(?:<p class="order-first[^"]*">([^<]*)</p>)?',
)
LINK_RE = re.compile(
    r'href="([^"]+)"[^>]*(?:\s|")*>\s*(Resume|Email|Portfolio|Instagram|LinkedIn|Vimeo|Youtube)</a>',
    re.DOTALL,
)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import urllib.request

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        page_html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    return page_html


def split_into_student_blocks(page_html):
    starts = [m.start() for m in re.finditer(r'<h2 class="text-theme-heading-color', page_html)]
    blocks = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(page_html)
        blocks.append(page_html[start:end])
    return blocks


def parse_students(page_html, program, year_label, source_url):
    students = []
    for block in split_into_student_blocks(page_html):
        name_match = NAME_RE.search(block)
        if not name_match:
            continue
        raw_name, class_year_text, specialization = name_match.groups()
        raw_name = html_module.unescape(raw_name).strip()
        specialization = html_module.unescape(specialization).strip() if specialization else ""

        if "," in raw_name:
            last, first = raw_name.split(",", 1)
            name = f"{first.strip()} {last.strip()}"
        else:
            name = raw_name

        links = {}
        for href, label in LINK_RE.findall(block):
            href = html_module.unescape(href.strip())
            links.setdefault(label, href)

        email = links.get("Email", "")
        if email.lower().startswith("mailto:"):
            email = email[len("mailto:"):].strip()

        portfolio_url = links.get("Portfolio") or links.get("Instagram") or links.get("Vimeo") or links.get("LinkedIn") or links.get("Youtube") or ""

        major = f"{program} ({year_label})"
        if specialization:
            major += f" — {specialization}"

        notes_parts = []
        if links.get("Resume"):
            notes_parts.append(f"Resume: {links['Resume']}")
        for label in ("Instagram", "LinkedIn", "Vimeo", "Youtube"):
            if label in links and links[label] != portfolio_url:
                notes_parts.append(f"{label}: {links[label]}")
        notes = "; ".join(notes_parts)

        students.append({
            "name": name,
            "email": email,
            "major": major,
            "graduation_year": "",
            "portfolio_url": portfolio_url,
            "college": "CalArts (Animation)",
            "notes": notes,
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape CalArts Film/Video Animation student portfolios (2026, Character + Experimental Animation)")
    parser.add_argument("--out", default="calarts_animation_students.csv")
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    all_students = []
    for path, program, year_label in PAGES:
        url = BASE_URL + path
        cache_path = os.path.join(CACHE_DIR, path.replace("/", "_") + ".html")
        page_html = fetch(url, cache_path, force_refresh=args.force_refresh)
        students = parse_students(page_html, program, year_label, url)
        print(f"{program} / {year_label}: {len(students)} students")
        all_students.extend(students)

    fieldnames = ["name", "email", "major", "graduation_year", "portfolio_url", "college", "notes"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in all_students:
            writer.writerow(s)

    with_email = sum(1 for s in all_students if s["email"])
    print(f"\nWrote {len(all_students)} total entries -> {args.out}")
    print(f"With email: {with_email} / {len(all_students)}")


if __name__ == "__main__":
    main()
