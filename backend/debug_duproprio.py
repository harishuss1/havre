"""
debug_duproprio.py — Verify DuProprio selectors against the live site.
Run from backend/:  python debug_duproprio.py
"""

import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

async def main():
    from playwright.async_api import async_playwright

    SEARCH_URL = "https://duproprio.com/en/search/list?search=true&for_sale=1&is_for_sale=1&parent=1"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"Loading {SEARCH_URL} ...")
        await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60_000)
        await asyncio.sleep(5)

        print("\n" + "="*60)
        print("  SELECTOR RESULTS")
        print("="*60)

        card_selectors = [
            "li.search-results-listings-list__item",
            "div.listing-item",
            "article[class*='listing']",
            "div[class*='listing-card']",
            "li[class*='result']",
        ]

        best_card = None
        print("\n── Finding listing cards ──")
        for sel in card_selectors:
            count = await page.locator(sel).count()
            mark = "✓" if count > 0 else "✗"
            print(f"  {mark}  {count:<5} {sel}")
            if count > 0 and not best_card:
                best_card = sel

        if not best_card:
            print("\n  No cards found. The page structure may have changed.")
            await browser.close()
            return

        print(f"\n  Using card selector: {best_card}")

        # Get first card HTML
        first_card = page.locator(best_card).first
        html = await first_card.inner_html()
        print(f"\n── First card HTML (first 1500 chars) ──\n{html[:1500]}")

        print("\n── Testing field selectors inside first card ──")
        fields = {
            "price":    ["span.price__amount", "div.price", "span[class*='price']", "div[class*='price']"],
            "address":  ["div.listing-address", "div[class*='address']", "address", "span[class*='address']"],
            "city":     ["span.city", "div.city", "span[class*='city']", "div[class*='municipality']"],
            "bedrooms": ["span[class*='bedroom']", "div[class*='bedroom']", "li[class*='bedroom']", "[data-characteristic='bedrooms'] span"],
            "link":     ["a[class*='link']", "a[href*='/en/']", "a.listing-thumbnail__link"],
        }

        for field, selectors in fields.items():
            print(f"\n  {field}:")
            for sel in selectors:
                try:
                    el = first_card.locator(sel).first
                    count = await first_card.locator(sel).count()
                    if count > 0:
                        text = (await el.inner_text())[:60].strip()
                        href = await el.get_attribute("href") if field == "link" else None
                        val = href or text
                        print(f"    ✓  {repr(val):<50} ← {sel}")
                    else:
                        print(f"    ✗              {sel}")
                except Exception:
                    print(f"    ✗              {sel}")

        print("\n" + "="*60)
        print("  Done. Update duproprio/selectors.py with working selectors.")
        print("="*60)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())