"""
deduplicator.py — Listing deduplication engine

Uses a content hash of key fields to detect:
  1. The exact same listing seen again on the same scrape cycle
  2. The same property listed on multiple sources (cross-source dedup)

The hash is stored on the listing record in the DB. Before saving,
we check if a listing with that hash already exists.
"""

import hashlib
import json
from .base import RawListing


def compute_hash(listing: RawListing) -> str:
    """
    Build a stable content hash for a listing.

    We hash: address + city + price + bedrooms + size_sqft.
    We deliberately exclude: listing_url, source, description, images.

    Why exclude those? The same property often appears on both Centris
    and DuProprio with different URLs and slightly different descriptions.
    The address + price + bedrooms combo is stable enough to catch duplicates
    across sources without being so strict that minor price changes
    re-trigger notifications.
    """
    key_fields = {
        "address": listing.address.strip().lower(),
        "city": listing.city.strip().lower(),
        "price": listing.price,
        "bedrooms": listing.bedrooms,
        "size_sqft": listing.size_sqft,
    }
    blob = json.dumps(key_fields, sort_keys=True)
    return hashlib.md5(blob.encode()).hexdigest()


def deduplicate(listings: list[RawListing]) -> list[RawListing]:
    """
    Remove duplicates from a batch of freshly scraped listings.
    This handles within-batch duplicates (same listing appearing on
    multiple pages of the same site in one scrape cycle).

    Cross-session dedup (already in DB?) is handled in the save layer.
    """
    seen: set[str] = set()
    unique: list[RawListing] = []

    for listing in listings:
        h = compute_hash(listing)
        if h not in seen:
            seen.add(h)
            unique.append(listing)

    removed = len(listings) - len(unique)
    if removed:
        print(f"[dedup] Removed {removed} within-batch duplicates")

    return unique