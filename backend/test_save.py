import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.scrapers.centris.scraper import CentrisScraper
from app.scrapers.base import SearchCriteria
from app.database import AsyncSessionLocal
from app.save import save_listings

async def scrape_data():
    scraper = CentrisScraper(headless=True, max_pages=1)
    criteria = SearchCriteria(
        min_price=300_000, max_price=600_000,
        min_bedrooms=2, cities=["Montreal"],
        property_types=["condo"], max_results=20,
    )
    print("Scraping...")
    return await scraper.run(criteria)

async def save_data(listings):
    print(f"Scraped {len(listings)} listings, saving to DB...")
    async with AsyncSessionLocal() as db:
        new = await save_listings(db, listings)
        await db.commit()
        print(f"Saved {len(new)} new listings to database")

def main():
    # 1. Playwright MUST use ProactorEventLoop on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    listings = asyncio.run(scrape_data())

    # 2. psycopg3 MUST use SelectorEventLoop on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(save_data(listings))

if __name__ == "__main__":
    main()