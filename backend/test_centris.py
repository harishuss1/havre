"""
test_centris.py — Manual scraper test
Run from the backend/ folder:

    cd backend
    python test_centris.py
"""

import asyncio
import sys
import os

# Make sure Python can find the app package
sys.path.insert(0, os.path.dirname(__file__))

from app.scrapers.centris.scraper import CentrisScraper
from app.scrapers.base import SearchCriteria


async def main():
    scraper = CentrisScraper(
        headless=False,  # Set True to run invisibly once you've verified it works
        max_pages=2,
    )

    criteria = SearchCriteria(
        min_price=300_000,
        max_price=900_000,
        cities=["Montreal"],
        max_results=100,
    )

    print("=" * 50)
    print("  Havre — Centris scraper test")
    print("=" * 50)

    try:
        listings = await scraper.run(criteria)
    except Exception as e:
        print(f"\n[ERROR] Scraper failed: {e}")
        raise

    print(f"\n{'=' * 50}")
    print(f"  Found {len(listings)} listings")
    print(f"{'=' * 50}\n")

    for i, l in enumerate(listings, 1):
        print(f"{i:02d}. [{l.property_type.upper()}] {l.address or '(no address)'}")
        print(f"     Price:    ${l.price:,}" if l.price else "     Price:    N/A")
        print(f"     Beds/Baths: {l.bedrooms}bd / {l.bathrooms}ba")
        print(f"     Size:     {l.size_sqft} sqft" if l.size_sqft else "     Size:     N/A")
        print(f"     URL:      {l.listing_url}")
        print()

    # ── outside the loop ──
    print("\n-- Searching for listing 18366795 --")
    match = next((l for l in listings if "18366795" in l.listing_url), None)
    if match:
        print(f"FOUND: {match.address} -- ${match.price:,}")
    else:
        print("Not found in this batch (may be on a later page)")

    if not listings:
        print("No listings returned. Try setting headless=False to watch the browser")
        print("and check if Centris is blocking the request or the selectors changed.")


if __name__ == "__main__":
    asyncio.run(main())