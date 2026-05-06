import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

async def main():
    from playwright.async_api import async_playwright
    SEARCH_URL = "https://www.kijiji.ca/b-real-estate/montreal/c34l80002"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
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
        print(f"Loading {SEARCH_URL} ...")
        await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60_000)
        print("Waiting 8s for JS...")
        await asyncio.sleep(8)
        print(f"Title: {await page.title()}")

        card_selectors = [
            "li[data-testid='listing-card-list-item']",
            "div[data-testid='listing-card']",
            "li[class*='regular-ad']", "div[class*='regular-ad']",
            "article", "li[class*='listing']", "div[class*='listing']",
            "[data-listing-id]", "[data-ad-id]",
            "li[class*='card']", "div[class*='card']",
        ]

        best_card = None
        print("\n── Cards ──")
        for sel in card_selectors:
            count = await page.locator(sel).count()
            mark = "✓" if count > 0 else "✗"
            print(f"  {mark}  {count:<5} {sel}")
            if count > 2 and not best_card:
                best_card = sel

        if not best_card:
            print("\nNo cards — dumping CSS classes...")
            classes = await page.evaluate("""() => {
                const s = new Set();
                document.querySelectorAll('[class]').forEach(e => {
                    if (typeof e.className === 'string')
                        e.className.split(' ').forEach(c => c && s.add(c));
                });
                return [...s].slice(0, 200);
            }""")
            for c in classes:
                print(f"  .{c}")
            await browser.close()
            return

        print(f"\nUsing: {best_card}")
        card = page.locator(best_card).first
        print(f"\nFirst card HTML:\n{(await card.inner_html())[:2000]}")

        for field, sels in {
            "price":   ["p[data-testid='listing-price']", "div[class*='price']", "span[class*='price']", "[class*='Price']"],
            "title":   ["h3[class*='title']", "h2[class*='title']", "a[class*='title']", "[class*='Title']"],
            "address": ["span[data-testid='listing-location']", "div[class*='location']", "span[class*='location']"],
            "link":    ["a[data-testid='listing-link']", "a[href*='/v-']", "a[class*='title']"],
        }.items():
            print(f"\n  {field}:")
            for sel in sels:
                count = await card.locator(sel).count()
                if count > 0:
                    el = card.locator(sel).first
                    val = await el.get_attribute("href") if field == "link" else (await el.inner_text())[:60]
                    print(f"    ✓  {repr(val.strip()):<50} ← {sel}")
                else:
                    print(f"    ✗              {sel}")

        await browser.close()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
asyncio.run(main())