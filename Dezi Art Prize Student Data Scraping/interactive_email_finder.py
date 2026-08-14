"""
Fallback tool for portfolio sites where a plain fetch or crawl4ai's passive
render finds no email, but a human clicking around the site would (e.g. a
"Contact" / "Reach out" link that reveals or constructs a mailto: only on
hover/click, common on Readymag/Webflow/Squarespace-style sites).

Drives a real Playwright browser: loads the page, hovers and clicks anything
that looks like a contact affordance, then dumps every mailto: href and any
visible email-shaped text found in the DOM afterward - both the passive state
and the post-interaction state, so you can see what only appeared after
clicking.

Usage:
    ../.venv_crawl4ai/Scripts/python.exe interactive_email_finder.py <url>
    ../.venv_crawl4ai/Scripts/python.exe interactive_email_finder.py <url> --screenshot out.png
"""
import argparse
import asyncio
import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w{2,}")
CONTACT_TEXT_RE = re.compile(
    r"contact|reach out|get in touch|say hello|email|contact me|hire me",
    re.IGNORECASE,
)
# platform/builder boilerplate addresses that show up in footers/widgets on
# hosted portfolio sites (Readymag, Squarespace, Wix, etc.) - never the
# person's own address, filter out so they don't get mistaken for a lead
PLATFORM_DOMAINS = {
    "readymag.com", "squarespace.com", "wix.com", "webflow.io", "webflow.com",
    "cargo.site", "format.com", "wordpress.com", "weebly.com",
}


PLACEHOLDER_EMAILS = {"user@domain.com", "name@example.com", "your@email.com", "email@example.com"}


def _is_platform_boilerplate(email):
    domain = email.split("@")[-1].lower()
    return domain in PLATFORM_DOMAINS or email.lower() in PLACEHOLDER_EMAILS


async def find_emails(url, screenshot_path=None, timeout_ms=15000):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        await page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        await page.wait_for_timeout(1500)

        passive_mailtos = await _extract_mailtos(page)
        passive_text_emails = set(EMAIL_RE.findall(await page.content()))

        # find and interact with anything that looks like a contact affordance
        candidates = await page.locator("a, button, [role=button]").all()
        interacted = 0
        for el in candidates:
            try:
                text = (await el.inner_text(timeout=1000)).strip()
            except Exception:
                continue
            if not text or not CONTACT_TEXT_RE.search(text):
                continue
            try:
                await el.hover(timeout=2000)
                await page.wait_for_timeout(500)
                await el.click(timeout=2000, trial=True)  # trial=True: don't navigate away
                interacted += 1
            except Exception:
                pass

        await page.wait_for_timeout(1000)
        post_mailtos = await _extract_mailtos(page)
        post_text_emails = set(EMAIL_RE.findall(await page.content()))

        if screenshot_path:
            await page.screenshot(path=screenshot_path, full_page=True)

        await browser.close()

        return {
            "passive_mailtos": passive_mailtos,
            "passive_text_emails": passive_text_emails,
            "post_interaction_mailtos": post_mailtos,
            "post_interaction_text_emails": post_text_emails,
            "contact_elements_found": interacted,
        }


async def _extract_mailtos(page):
    hrefs = await page.eval_on_selector_all(
        "a[href^='mailto:']", "els => els.map(e => e.getAttribute('href'))"
    )
    mailtos = set()
    for href in hrefs:
        m = EMAIL_RE.search(href.replace("mailto:", ""))
        if m:
            mailtos.add(m.group(0))
    return mailtos


def main():
    parser = argparse.ArgumentParser(description="Interactively probe a portfolio page for an email")
    parser.add_argument("url")
    parser.add_argument("--screenshot", default=None, help="optional path to save a full-page screenshot")
    parser.add_argument("--timeout", type=int, default=15000)
    args = parser.parse_args()

    result = asyncio.run(find_emails(args.url, screenshot_path=args.screenshot, timeout_ms=args.timeout))

    print(f"Contact-like elements found and interacted with: {result['contact_elements_found']}")
    print(f"\nmailto: links present before interaction: {result['passive_mailtos'] or '(none)'}")
    print(f"mailto: links present after hover/click: {result['post_interaction_mailtos'] or '(none)'}")

    new_mailtos = result["post_interaction_mailtos"] - result["passive_mailtos"]
    if new_mailtos:
        print(f"\n>>> NEW mailto: links revealed only after interaction: {new_mailtos}")

    new_text = result["post_interaction_text_emails"] - result["passive_text_emails"]
    if new_text:
        print(f">>> NEW email-shaped text revealed only after interaction: {new_text}")

    all_found = result["passive_mailtos"] | result["post_interaction_mailtos"] | result["post_interaction_text_emails"]
    filtered = {e for e in all_found if not _is_platform_boilerplate(e)}
    boilerplate = all_found - filtered
    if filtered:
        print(f"\nCandidate emails (platform boilerplate excluded): {filtered}")
        if boilerplate:
            print(f"(excluded as site-builder boilerplate: {boilerplate})")
    elif all_found:
        print(f"\nOnly platform boilerplate addresses found, no personal email: {all_found}")
    else:
        print("\nNo email found via mailto: hrefs or visible text, even after interaction.")
        print("If a human can find it (e.g. via 'copy email address' on a hover-revealed link),")
        print("the address may be constructed by JS on click rather than present as plain text/href -")
        print("would need a person to manually copy it, or a screenshot + closer DOM inspection.")


if __name__ == "__main__":
    main()
