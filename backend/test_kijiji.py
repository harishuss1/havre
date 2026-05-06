import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.scrapers.kijiji.scraper import KijijiScraper
from app.scrapers.base import SearchCriteria

async def main():
    scraper = KijijiScraper(headless=False, max_pages=1)
    criteria = SearchCriteria(
        min_price=300_000, max_price=800_000,
        cities=["Montreal"], max_results=20,
    )
    listings = await scraper.run(criteria)
    print(f"\nFound {len(listings)} listings")
    for l in listings[:10]:
        print(f"  ${l.price:>10,}  [{l.property_type:8}] {l.address[:35]}  {l.city}")

    print("\n-- Raw URLs for debugging --")
    for l in listings:
        print(f"  {l.listing_url}")

asyncio.run(main())
