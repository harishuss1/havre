"""
Dump the first Kijiji listing card HTML in full to verify all field selectors.
"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

URL = "https://www.kijiji.ca/b-real-estate/montreal/c34l80002"

def safe(s):
    return str(s).encode('ascii', errors='replace').decode()

async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="en-CA",
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = await context.new_page()

        print(f"Loading {URL} ...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        print("Waiting 15s...")
        await asyncio.sleep(15)

        # Use starts-with selector for listing cards
        LISTING_CARD = "li[data-testid^='listing-card-list-item']"
        count = await page.locator(LISTING_CARD).count()
        print(f"\nCards found with '{LISTING_CARD}': {count}")

        if count > 0:
            print("\n-- First card full HTML --")
            html = await page.locator(LISTING_CARD).first.inner_html()
            print(safe(html[:5000]))

            print("\n-- Field selectors on first card --")
            card = page.locator(LISTING_CARD).first
            for field, sels in {
                "price":    ["p[data-testid='listing-price']", "[data-testid='listing-price']", "span[class*='price']", "div[class*='price']"],
                "title":    ["h3[class*='title']", "h2[class*='title']", "[class*='listing-title']", "h3", "h2"],
                "address":  ["span[data-testid='listing-location']", "[data-testid='listing-location']", "[class*='location']"],
                "link":     ["a[data-testid='listing-link']", "[data-testid='listing-link']", "a[href*='/v-']", "a"],
                "image":    ["img", "[data-testid='listing-card-image-container'] img"],
                "bedrooms": ["span[data-testid='bedrooms']", "[data-testid='bedrooms']", "[class*='bedroom']"],
            }.items():
                print(f"\n  {field}:")
                for sel in sels:
                    try:
                        c = await card.locator(sel).count()
                        if c > 0:
                            el = card.locator(sel).first
                            if field == "link":
                                val = await el.get_attribute("href")
                            elif field == "image":
                                val = await el.get_attribute("src")
                            else:
                                val = await el.inner_text()
                            print(f"    YES  {repr(safe(str(val).strip())):<50}  <- {sel}")
                        else:
                            print(f"     no                                                    <- {sel}")
                    except Exception as ex:
                        print(f"    ERR  {ex}  <- {sel}")

        await browser.close()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
asyncio.run(main())
