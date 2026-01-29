import argparse
import asyncio
import csv
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

DEFAULT_SEED_URL = "https://www.artistsfuturesfund.org/funding-directory"

JS_HEAVY_MARKERS = [
    "__NEXT_DATA__",
    "window.__NUXT__",
    "data-reactroot",
    "id=\"__next\"",
    "id=\"app\"",
    "ng-version",
    "data-hydrate",
]

class LinkParser(HTMLParser):
    def __init__(self, require_entry_content=True):
        super().__init__()
        self.links = []
        self.base_href = ""
        self._in_entry_content = False
        self._entry_depth = 0
        self._require_entry_content = require_entry_content
        if not require_entry_content:
            self._in_entry_content = True
            self._entry_depth = 1
        self._in_heading = False
        self._heading_text = []
        self._stop_after_heading = False
        self._in_a = False
        self._current_href = ""
        self._current_text = []
        self._current_title = ""
        self._current_aria = ""
        self._current_img_alt = ""

    def handle_starttag(self, tag, attrs):
        tag_l = tag.lower()
        if tag_l == "base":
            for k, v in attrs:
                if k.lower() == "href":
                    self.base_href = v or ""
                    break
        if tag_l in ("div", "section", "article"):
            found_entry = False
            for k, v in attrs:
                if k.lower() == "class" and v:
                    classes = v.split()
                    if "entry-content" in classes:
                        self._in_entry_content = True
                        self._entry_depth = 1
                        found_entry = True
                        break
            if self._in_entry_content and not found_entry:
                self._entry_depth += 1
        if tag_l in ("h1", "h2", "h3"):
            self._in_heading = True
            self._heading_text = []
        if tag_l == "a":
            self._in_a = True
            self._current_href = ""
            self._current_text = []
            self._current_title = ""
            self._current_aria = ""
            self._current_img_alt = ""
            for k, v in attrs:
                key = k.lower()
                if key == "href":
                    self._current_href = v or ""
                elif key == "title":
                    self._current_title = v or ""
                elif key == "aria-label":
                    self._current_aria = v or ""
        if tag_l == "img" and self._in_a:
            for k, v in attrs:
                if k.lower() == "alt":
                    self._current_img_alt = v or ""
                    break

    def handle_data(self, data):
        if self._in_heading:
            self._heading_text.append(data)
        if self._in_a:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() in ("h1", "h2", "h3") and self._in_heading:
            heading_text = " ".join("".join(self._heading_text).split()).lower()
            if self._require_entry_content and heading_text == "testimonials":
                self._stop_after_heading = True
            self._in_heading = False
            self._heading_text = []
        if tag.lower() == "a" and self._in_a:
            text = "".join(self._current_text).strip()
            href = self._current_href.strip()
            if href and self._in_entry_content and not self._stop_after_heading:
                self.links.append(
                    (
                        href,
                        text,
                        self._current_title.strip(),
                        self._current_aria.strip(),
                        self._current_img_alt.strip(),
                    )
                )
            self._in_a = False
            self._current_href = ""
            self._current_text = []
            self._current_title = ""
            self._current_aria = ""
            self._current_img_alt = ""
        if tag.lower() in ("div", "section", "article") and self._in_entry_content:
            self._entry_depth -= 1
            if self._entry_depth <= 0:
                self._in_entry_content = False
                self._entry_depth = 0


def is_js_heavy(html):
    html_lower = html.lower()
    if any(marker.lower() in html_lower for marker in JS_HEAVY_MARKERS):
        return True
    script_count = html_lower.count("<script")
    text_only = re.sub(r"<[^>]+>", "", html)
    text_len = len(re.sub(r"\s+", " ", text_only).strip())
    if script_count > 20 and text_len < 2000:
        return True
    return False


def fetch_html_requests(url):
    import urllib.request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")


async def fetch_html_crawl4ai(url, render_js):
    try:
        from crawl4ai import AsyncWebCrawler
    except Exception as exc:
        raise RuntimeError("crawl4ai is not installed") from exc

    # Minimal crawl4ai usage; adjust config for JS-heavy pages if supported.
    async with AsyncWebCrawler() as crawler:
        if render_js:
            # Some crawl4ai versions support passing config or render flags.
            result = await crawler.arun(url, render_js=True)
        else:
            result = await crawler.arun(url)
        return result.html


def extract_orgs(seed_url, html, dedupe):
    parser = LinkParser(require_entry_content=True)
    parser.feed(html)
    if not parser.links:
        parser = LinkParser(require_entry_content=False)
        parser.feed(html)
    orgs = []
    base_url = parser.base_href.strip() or seed_url
    seed_host = urlparse(base_url).netloc.lower()

    seen = set() if dedupe else None
    for href, text, title, aria_label, img_alt in parser.links:
        href = (href or "").strip()
        if not href:
            continue
        if href.startswith("#") or href.lower().startswith("mailto:") or href.lower().startswith("tel:"):
            continue
        if href.lower().startswith("javascript:"):
            continue
        full_url = urljoin(base_url, href)
        norm = full_url.strip()
        parsed = urlparse(norm)
        if not parsed.scheme.startswith("http"):
            continue
        host = parsed.netloc.lower()
        if not host or host == seed_host:
            continue
        key = norm if dedupe else None
        if seen is not None:
            if key in seen:
                continue
            seen.add(key)
        link_name = (text or "").strip() or (aria_label or "").strip() or (title or "").strip() or (img_alt or "").strip()
        if not link_name:
            link_name = host
        orgs.append({
            "org_name": link_name,
            "org_website": norm,
            "org_type": "",
            "source_link": seed_url,
            "source_type": "A",
            "access_status": "open",
            "opportunity_types_offered": "",
            "geographic_focus": "",
            "mediums_supported": "",
            "estimated_opp_count": "unknown",
            "priority": "",
            "notes": "Seed directory external link; verify org and opportunity scope.",
            "date_extracted": datetime.now(timezone.utc).date().isoformat(),
        })
    return orgs


def write_csv(rows, out_path):
    if not rows:
        return
    fieldnames = [
        "org_name",
        "org_website",
        "org_type",
        "source_link",
        "source_type",
        "access_status",
        "opportunity_types_offered",
        "geographic_focus",
        "mediums_supported",
        "estimated_opp_count",
        "priority",
        "notes",
        "date_extracted",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Phase 1 seed link extractor (test)")
    parser.add_argument("--seed", default=DEFAULT_SEED_URL, help="Seed URL to extract links from")
    parser.add_argument("--out", default="ORG_MASTER_LIST_TEST.csv", help="Output CSV path")
    parser.add_argument("--dedupe", action="store_true", help="Dedupe identical links (off by default)")
    args = parser.parse_args()

    seed_url = args.seed

    # First fetch via simple request to detect JS heaviness.
    html = fetch_html_requests(seed_url)
    js_heavy = is_js_heavy(html)

    # Use crawl4ai for final fetch, with JS rendering if needed.
    try:
        html = asyncio.run(fetch_html_crawl4ai(seed_url, render_js=js_heavy))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        print("Install crawl4ai before running this script.", file=sys.stderr)
        sys.exit(1)

    orgs = extract_orgs(seed_url, html, dedupe=args.dedupe)
    write_csv(orgs, args.out)
    print(f"Seed: {seed_url}")
    print(f"JS-heavy: {'yes' if js_heavy else 'no'}")
    print(f"Orgs written: {len(orgs)} -> {args.out}")


if __name__ == "__main__":
    main()
