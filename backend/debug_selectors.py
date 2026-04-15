"""
debug_selectors.py — Centris selector inspector

Opens Centris in a visible browser window and tries every selector,
printing what it finds so we can update selectors.py with the real values.

Run from backend/:
    python debug_selectors.py
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from playwright.async_api import async_playwright

URL = "https://www.centris.ca/en/properties~for-sale~montreal"

# Candidate selectors to test — we'll find which ones actually work
CANDIDATES = {
    "listing_card": [
        "div.shell",
        "div.property-thumbnail-item",
        "article.property-thumbnail-item",
        "[data-id]",
        "div[class*='property']",
        "div[class*='listing']",
    ],
    "price": [
        "div.price span",
        "span.price",
        "div.price",
        "span[class*='price']",
        "div[class*='price'] span",
        "p.price",
    ],
    "address": [
        "div.address span:first-child",
        "div.address",
        "span.address",
        "div[class*='address']",
        "p.address",
        "div.location",
        "span[class*='address']",
    ],
    "city": [
        "div.address span.region",
        "span.region",
        "div.address span:last-child",
        "div.location span",
        "span[class*='region']",
        "span[class*='city']",
    ],
    "bedrooms": [
        "div.cac",
        "span.cac",
        "div[class*='bedroom']",
        "span[class*='bed']",
        "div[class*='cac']",
        "li[class*='bedroom']",
        "div.icon-bed ~ span",
    ],
    "bathrooms": [
        "div.sdb",
        "span.sdb",
        "div[class*='bathroom']",
        "span[class*='bath']",
        "div[class*='sdb']",
        "li[class*='bathroom']",
    ],
    "property_type": [
        "div.listing-type span",
        "span[class*='type']",
        "div[class*='type']",
        "span.property-type",
        "div.property-type",
        "span[class*='category']",
    ],
    "area": [
        "div.usable-area",
        "span[class*='area']",
        "div[class*='area']",
        "span[class*='sqft']",
        "span[class*='superficie']",
        "div.superficie",
    ],
    "link": [
        "a.a-more-detail",
        "a[class*='detail']",
        "a[href*='/en/']",
        "div.shell a",
        "article a",
    ],
}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="fr-CA",
        )
        page = await context.new_page()

        print(f"Loading {URL} ...")
        await page.goto(URL, wait_until="networkidle", timeout=30_000)
        await asyncio.sleep(3)  # Let JS render

        print("\n" + "=" * 60)
        print("  SELECTOR RESULTS")
        print("=" * 60)

        # First find which card selector works
        print("\n── Finding listing cards ──")
        working_card_sel = None
        for sel in CANDIDATES["listing_card"]:
            cards = await page.query_selector_all(sel)
            status = f"✓  {len(cards)} cards" if cards else "✗  0"
            print(f"  {status:20s}  {sel}")
            if cards and not working_card_sel:
                working_card_sel = sel

        if not working_card_sel:
            print("\n[!] No card selector worked — Centris may have changed their HTML.")
            print("    Check the browser window and use DevTools to inspect the listing cards.")
            await asyncio.sleep(30)
            await browser.close()
            return

        print(f"\n  Using card selector: {working_card_sel}")
        cards = await page.query_selector_all(working_card_sel)
        first_card = cards[0] if cards else None

        # Print the raw HTML of the first card so we can inspect it
        if first_card:
            html = await first_card.inner_html()
            print(f"\n── First card HTML (first 1500 chars) ──")
            print(html[:1500])
            print("...")

        # Test all other selectors inside the first card
        print("\n── Testing field selectors inside first card ──")
        for field, selectors in CANDIDATES.items():
            if field == "listing_card":
                continue
            print(f"\n  {field}:")
            for sel in selectors:
                try:
                    if first_card:
                        el = await first_card.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            print(f"    ✓  '{text.strip()[:60]}'  ← {sel}")
                        else:
                            print(f"    ✗              {sel}")
                    else:
                        # Fall back to page-level
                        el = await page.query_selector(sel)
                        text = (await el.inner_text()) if el else ""
                        status = f"✓  '{text.strip()[:40]}'" if el else "✗"
                        print(f"    {status:45s}  {sel}")
                except Exception as e:
                    print(f"    !  Error: {e}  ← {sel}")

        # Also intercept network requests to find the real filter API
        print("\n" + "=" * 60)
        print("  NETWORK: watching for API calls (applying a manual filter)...")
        print("  Try clicking a filter in the browser window now.")
        print("  We'll capture any POST/fetch requests for 20 seconds.")
        print("=" * 60)

        api_calls = []

        async def capture_request(request):
            if request.method == "POST" and "centris" in request.url:
                api_calls.append({
                    "url": request.url,
                    "method": request.method,
                    "post_data": request.post_data,
                })

        page.on("request", capture_request)
        await asyncio.sleep(20)

        if api_calls:
            print("\n── Captured API calls ──")
            for call in api_calls:
                print(f"\n  URL:  {call['url']}")
                print(f"  Data: {call['post_data'][:200] if call['post_data'] else 'none'}")
        else:
            print("\n  No POST calls captured.")

        await browser.close()

        print("\n" + "=" * 60)
        print("  Done. Update selectors.py with the working selectors above.")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())