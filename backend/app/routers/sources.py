"""
routers/sources.py — Scraper source management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.source import Source

router = APIRouter(prefix="/sources", tags=["sources"])


class SourceOut(BaseModel):
    id: str
    name: str
    display_name: str
    is_enabled: bool
    scrape_interval_minutes: int
    last_scraped_at: datetime | None
    total_listings_found: int
    model_config = {"from_attributes": True}


@router.get("", response_model=list[SourceOut])
async def get_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.name))
    return result.scalars().all()


@router.post("/{name}/trigger", status_code=202)
async def trigger_scrape(name: str, db: AsyncSession = Depends(get_db)):
    """Manually triggers an immediate scrape for a given source."""
    result = await db.execute(select(Source).where(Source.name == name))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{name}' not found")
    if not source.is_enabled:
        raise HTTPException(status_code=400, detail=f"Source '{name}' is disabled")

    # Import here to avoid circular imports at startup
    from ..tasks.scrape_tasks import scrape_source
    scrape_source.delay(name)

    return {"message": f"Scrape triggered for {name}"}