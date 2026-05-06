"""
test_save_pipeline.py — End-to-end scrape → deduplicate → save → verify

Runs all three scrapers for Greater Montreal, saves results to Postgres,
and prints a DB summary. No API or Celery needed — tests the save layer directly.

Run from the backend/ folder:
    cd backend
    python test_save_pipeline.py

Make sure Docker is running first:
    docker-compose up -d
"""

import asyncio
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))

# Windows event loop conflict:
#   Playwright subprocess management → requires ProactorEventLoop
#   psycopg3 async                   → requires SelectorEventLoop
#
# Solution: run in two phases, switching policy between asyncio.run() calls.
# asyncio.run() creates a fresh event loop each time, so the switch is clean.

from sqlalchemy import select, func

from app.database import engine, AsyncSessionLocal, Base
from app.models.listing import Listing
from app.scrapers.base import SearchCriteria
from app.scrapers.centris.scraper import CentrisScraper
from app.scrapers.duproprio.scraper import DuProprioScraper
from app.scrapers.kijiji.scraper import KijijiScraper
from app.scrapers.deduplicator import deduplicate
from app.save import save_listings


# ── Default search criteria ────────────────────────────────────────────────────
#
# Covers Greater Montreal (~55km radius). Each scraper interprets "cities"
# differently for URL construction, but all three naturally return results
# across the island + south/north shore when given "Montreal":
#
#   Centris   — "montreal" city slug → Island + surrounding boroughs
#   DuProprio — city_name=Montreal   → Montreal island listings
#   Kijiji    — uses Grand Montreal region URL regardless of cities list
#
# min_price=150_000 filters out parking spots, storage units, fractions.
# max_pages=3 keeps each scraper run under ~2 minutes.

MONTREAL_CRITERIA = SearchCriteria(
    cities=["Montreal"],
    min_price=150_000,
    max_results=200,
)

SCRAPERS = [
    ("Centris",    CentrisScraper(headless=True,  max_pages=3)),
    ("DuProprio",  DuProprioScraper(headless=True, max_pages=3)),
    ("Kijiji",     KijijiScraper(headless=True,    max_pages=3)),
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def line(char="=", n=55):
    print(char * n)


async def ensure_tables():
    """Create tables if they don't exist (dev shortcut — Alembic handles prod)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB tables ready.")


async def run_scraper(name: str, scraper, criteria: SearchCriteria) -> int:
    """Run one scraper, dedup, save. Returns count of new listings saved."""
    line()
    print(f"  Scraping {name}...")
    line()
    try:
        listings = await scraper.run(criteria)
        unique   = deduplicate(listings)

        async with AsyncSessionLocal() as db:
            new = await save_listings(db, unique)
            await db.commit()

        print(
            f"[{name}] scraped={len(listings)}  "
            f"unique={len(unique)}  "
            f"new saved={len(new)}"
        )
        return len(new)

    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        traceback.print_exc()
        return 0


async def print_db_summary():
    """Query DB and print a breakdown by source."""
    line()
    print("  Database summary")
    line()

    async with AsyncSessionLocal() as db:
        # Per-source counts
        rows = (await db.execute(
            select(Listing.source, func.count(Listing.id))
            .group_by(Listing.source)
            .order_by(Listing.source)
        )).all()

        for source, count in rows:
            print(f"  {source:<12} {count:>5} listings")

        # Total
        total = (await db.execute(select(func.count(Listing.id)))).scalar_one()
        line("-")
        print(f"  {'TOTAL':<12} {total:>5} listings")

        # Sample — 5 most recent
        sample = (await db.execute(
            select(Listing)
            .order_by(Listing.first_seen_at.desc())
            .limit(5)
        )).scalars().all()

        if sample:
            print("\n  5 most recent listings:")
            for l in sample:
                addr = (l.address or l.city or "?")[:38]
                print(f"    [{l.source:<10}] ${l.price:>9,}  {addr}")


# ── Main ───────────────────────────────────────────────────────────────────────

# ── Phase 1: Scrape (Playwright → needs ProactorEventLoop on Windows) ──────────

async def phase1_scrape() -> list:
    """Run all scrapers and return combined RawListing list."""
    from app.scrapers.deduplicator import deduplicate

    print("\nHavre — Save Pipeline Test")
    line()
    print("Phase 1: Scraping all sources...")

    all_listings = []
    for name, scraper in SCRAPERS:
        line()
        print(f"  {name}")
        line()
        try:
            listings = await scraper.run(MONTREAL_CRITERIA)
            print(f"[{name}] scraped {len(listings)} listings")
            all_listings.extend(listings)
        except Exception as e:
            print(f"[{name}] ERROR: {e}")
            traceback.print_exc()

    unique = deduplicate(all_listings)
    print(f"\nTotal scraped: {len(all_listings)}  After cross-source dedup: {len(unique)}")
    return unique


# ── Phase 2: Save + verify (psycopg3 → needs SelectorEventLoop on Windows) ────

async def phase2_save(listings: list) -> None:
    """Create tables, save listings, print DB summary."""
    print("\nPhase 2: Saving to database...")

    await ensure_tables()

    async with AsyncSessionLocal() as db:
        new = await save_listings(db, listings)
        await db.commit()
        print(f"New listings saved: {len(new)}  (skipped {len(listings) - len(new)} already in DB)")

    await print_db_summary()
    await engine.dispose()


# ── Entry point ────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    # Phase 1 — Playwright (ProactorEventLoop)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    scraped = asyncio.run(phase1_scrape())

    # Phase 2 — psycopg3 (SelectorEventLoop)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(phase2_save(scraped))
else:
    async def main():
        scraped = await phase1_scrape()
        await phase2_save(scraped)
    asyncio.run(main())
