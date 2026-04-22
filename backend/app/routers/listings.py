"""
routers/listings.py — Listing endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.listing import Listing

router = APIRouter(prefix="/listings", tags=["listings"])


# ── Response schema ────────────────────────────────────────────────────────────

class ListingOut(BaseModel):
    id: str
    source: str
    external_id: str
    title: str
    address: str
    city: str
    region: str
    postal_code: str
    price: int
    bedrooms: int | None
    bathrooms: int | None
    size_sqft: int | None
    property_type: str
    listing_url: str
    images: list
    description: str
    content_hash: str
    first_seen_at: datetime
    last_seen_at: datetime

    model_config = {"from_attributes": True}


class PaginatedListings(BaseModel):
    total: int
    page: int
    per_page: int
    results: list[ListingOut]


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedListings)
async def get_listings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: str | None = Query(None),
    city: str | None = Query(None),
    min_price: int | None = Query(None),
    max_price: int | None = Query(None),
    min_bedrooms: int | None = Query(None),
    property_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Listing).order_by(Listing.first_seen_at.desc())

    if source:
        query = query.where(Listing.source == source)
    if city:
        query = query.where(Listing.city.ilike(f"%{city}%"))
    if min_price is not None:
        query = query.where(Listing.price >= min_price)
    if max_price is not None:
        query = query.where(Listing.price <= max_price)
    if min_bedrooms is not None:
        query = query.where(Listing.bedrooms >= min_bedrooms)
    if property_type:
        query = query.where(Listing.property_type == property_type)

    # Total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Paginated results
    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    listings = result.scalars().all()

    return PaginatedListings(total=total, page=page, per_page=per_page, results=listings)


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing