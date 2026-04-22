"""
tasks/scrape_tasks.py — Celery scrape tasks (Phase 3)
Stub file so imports don't break before Celery is wired up.
"""

def scrape_source(source_name: str):
    """
    Placeholder — will be a proper Celery task in Phase 3.
    For now, runs the scraper synchronously.
    """
    import asyncio
    from app.scrapers import get_scraper
    from app.scrapers.base import SearchCriteria

    async def _run():
        from app.database import AsyncSessionLocal
        from app.save import save_listings

        scraper = get_scraper(source_name)
        criteria = SearchCriteria(cities=["Montreal"], max_results=100)
        listings = await scraper.run(criteria)

        async with AsyncSessionLocal() as db:
            new = await save_listings(db, listings)
            await db.commit()
            print(f"[task] {source_name}: {len(new)} new listings saved")

    asyncio.run(_run())


# Make .delay() work as a no-op until Celery is set up
scrape_source.delay = scrape_source