"""
routers/stats.py — Dashboard summary stats
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..models.listing import Listing
from ..models.source import Source

router = APIRouter(prefix="/stats", tags=["stats"])


class StatsOut(BaseModel):
    total_listings: int
    new_today: int
    sources_active: int
    sources_total: int


@router.get("", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total = (await db.execute(select(func.count()).select_from(Listing))).scalar_one()
    new_today = (await db.execute(
        select(func.count()).select_from(Listing).where(Listing.first_seen_at >= today)
    )).scalar_one()
    sources_total = (await db.execute(select(func.count()).select_from(Source))).scalar_one()
    sources_active = (await db.execute(
        select(func.count()).select_from(Source).where(Source.is_enabled == True)
    )).scalar_one()

    return StatsOut(
        total_listings=total,
        new_today=new_today,
        sources_active=sources_active,
        sources_total=sources_total,
    )