import argparse
import csv
import os
import re

URL = "https://art.wisc.edu/people/graduate-students/"
CACHE_PATH = os.path.join("..", "cache", "uw_madison", "graduate-students.html")

# Each student entry on the page: Name, then "MFA 'YY", then optional email,
# then optional pronouns, then optional "Follow" link. The previous entry's
# trailing "She/Her Follow" text runs directly into the next name with no
# delimiter, so strip any such leading noise from the captured name.
ENTRY_RE = re.compile(
    r"([A-Z][^,]*?)\s+MFA\s*(?:&#8217;|')?(\d{2})\s*"
    r"([\w.+-]+@wisc\.edu)?"
)
LEADING_NOISE_RE = re.compile(
    r"^(?:(?:He|She|They)/(?:Him|Her|Them|They)\s+)?(?:Follow\s+)?"
)


def fetch(url, cache_path, force_refresh=False):
    if not force_refresh and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    import ssl
    import urllib.request

    # art.wisc.edu's TLS certificate is expired on their end (confirmed via
    # openssl/curl) — this is a public, read-only page with no sensitive data
    # exchanged, so we skip cert verification only for this one known host
    # rather than leaving the source unscraped.
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15, context=context) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def parse_students(html):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL)
    text_plain = re.sub("<[^>]+>", " ", text)
    text_plain = re.sub(r"\s+", " ", text_plain)

    start = text_plain.find("GRADUATE STUDENTS")
    end = text_plain.find("Facilities", start + 200) if start != -1 else -1
    segment = text_plain[start + len("GRADUATE STUDENTS"):end] if start != -1 and end != -1 else ""

    students = []
    for m in ENTRY_RE.finditer(segment):
        name = LEADING_NOISE_RE.sub("", m.group(1).strip()).strip()
        year_suffix = m.group(2)
        email = (m.group(3) or "").strip()

        graduation_year = f"20{year_suffix}"

        students.append({
            "name": name,
            "email": email,
            "major": "MFA",
            "graduation_year": graduation_year,
            "portfolio_url": "",
            "college": "UW-Madison",
            "notes": "" if email else "No email published on directory page",
        })
    return students


def main():
    parser = argparse.ArgumentParser(description="Scrape UW-Madison Art current graduate students directory")
    parser.add_argument("--out", default="uw_madison_students.csv")
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

    missing_email = sum(1 for s in students if not s["email"])
    print(f"Wrote {len(students)} students -> {args.out}")
    print(f"Missing email: {missing_email}")


if __name__ == "__main__":
    main()
