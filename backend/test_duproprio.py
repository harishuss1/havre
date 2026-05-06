import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.scrapers.duproprio.scraper import DuProprioScraper
from app.scrapers.base import SearchCriteria

async def main():
    scraper = DuProprioScraper(headless=False, max_pages=1)
    criteria = SearchCriteria(
        min_price=300_000, max_price=800_000,
        cities=["Montreal"], max_results=20,
    )
    listings = await scraper.run(criteria)
    print(f"\nFound {len(listings)} listings")
    for l in listings[:5]:
        print(f"  [{l.property_type}] {l.address}, {l.city} — ${l.price:,}")
        
    print("\n-- Raw URLs for debugging --")
    for l in listings:
        print(f"  {l.listing_url}")

asyncio.run(main())