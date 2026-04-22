"""
save.py — Saves scraped RawListings to the database.

This is the bridge between the scraping engine and the database.
It handles cross-session deduplication (hash already in DB? skip it)
and returns which listings are genuinely new so the notification
system can act on them.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.listing import Listing
from .scrapers.base import RawListing
from .scrapers.deduplicator import compute_hash


async def save_listings(
    db: AsyncSession,
    raw_listings: list[RawListing],
) -> list[Listing]:
    """
    Saves a batch of scraped listings to the database.
    Skips any listing whose content_hash already exists (already seen).
    Returns only the listings that were genuinely new and saved.
    """
    if not raw_listings:
        return []

    # Compute hashes for all incoming listings
    hashes = [compute_hash(r) for r in raw_listings]

    # Check which hashes already exist in the DB in one query
    result = await db.execute(
        select(Listing.content_hash).where(Listing.content_hash.in_(hashes))
    )
    existing_hashes = {row[0] for row in result.fetchall()}

    new_listings: list[Listing] = []

    for raw, content_hash in zip(raw_listings, hashes):
        if content_hash in existing_hashes:
            continue  # Already in DB — skip

        listing = Listing(
            source=raw.source,
            external_id=raw.external_id,
            title=raw.title,
            address=raw.address,
            city=raw.city,
            region=raw.region,
            postal_code=raw.postal_code,
            price=raw.price,
            bedrooms=raw.bedrooms,
            bathrooms=raw.bathrooms,
            size_sqft=raw.size_sqft,
            property_type=raw.property_type,
            listing_url=raw.listing_url,
            images=raw.images,
            description=raw.description,
            content_hash=content_hash,
        )
        db.add(listing)
        new_listings.append(listing)

    if new_listings:
        await db.flush()  # assigns IDs without committing
        print(f"[save] Saved {len(new_listings)} new listings "
              f"(skipped {len(raw_listings) - len(new_listings)} duplicates)")

    return new_listings