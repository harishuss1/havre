"""
routers/profiles.py — Search profile endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.search_profile import SearchProfile

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileIn(BaseModel):
    name: str
    min_price: int | None = None
    max_price: int | None = None
    min_bedrooms: int | None = None
    cities: list[str] = []
    property_types: list[str] = []
    sources: list[str] = []
    is_active: bool = True


class ProfileOut(ProfileIn):
    id: str
    created_at: datetime
    model_config = {"from_attributes": True}


@router.get("", response_model=list[ProfileOut])
async def get_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchProfile).order_by(SearchProfile.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ProfileOut, status_code=201)
async def create_profile(data: ProfileIn, db: AsyncSession = Depends(get_db)):
    profile = SearchProfile(**data.model_dump())
    db.add(profile)
    await db.flush()
    return profile


@router.put("/{profile_id}", response_model=ProfileOut)
async def update_profile(profile_id: str, data: ProfileIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in data.model_dump().items():
        setattr(profile, key, value)
    return profile


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchProfile).where(SearchProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)