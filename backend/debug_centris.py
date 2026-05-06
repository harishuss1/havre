"""
Centris filter + pagination debug:
- Intercepts real network requests to find the actual filter API
- Tests pagination wait strategy
"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

def safe(s):
    return str(s).encode('ascii', errors='replace').decode()

async def main():
    from playwright.async_api import async_playwright
    from app.scrapers.centris.selectors import SEARCH_PAGE_URL, LISTING_CARD, PAGINATION_NEXT

    api_calls = []

    async def capture_request(req):
        if req.method == "POST" and "centris.ca" in req.url:
            try:
                body = req.post_data or ""
            except Exception:
                body = ""
            api_calls.append({"url": req.url, "body": body[:300]})

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1440, "height": 900},
            locale="fr-CA",
        )
        page = await context.new_page()
        page.on("request", capture_request)

        url = SEARCH_PAGE_URL.format(city="montreal")
        print(f"Loading: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await asyncio.sleep(3)

        print(f"\nPOST calls captured on initial load ({len(api_calls)}):")
        for c in api_calls[:10]:
            print(f"  {safe(c['url'])}")
            if c['body']:
                print(f"    body: {safe(c['body'][:200])}")

        api_calls.clear()

        # Test pagination
        print("\n-- Testing pagination --")
        cards_before = await page.locator(LISTING_CARD).count()
        print(f"Cards before click: {cards_before}")

        next_btn = await page.query_selector(PAGINATION_NEXT)
        if next_btn:
            print("Clicking next...")
            await next_btn.click()
            # Try domcontentloaded + wait for cards instead of networkidle
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=15_000)
            except Exception as e:
                print(f"domcontentloaded timeout (ok): {e}")
            await asyncio.sleep(4)
            cards_after = await page.locator(LISTING_CARD).count()
            print(f"Cards after click: {cards_after}")
            print(f"Current URL: {safe(page.url)}")

            print(f"\nPOST calls during pagination ({len(api_calls)}):")
            for c in api_calls[:10]:
                print(f"  {safe(c['url'])}")
                if c['body']:
                    print(f"    body: {safe(c['body'][:200])}")
        else:
            print("No next button found")

        await browser.close()

asyncio.run(main())
