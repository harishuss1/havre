"""
models/search_profile.py — Search profile model
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Price range (either can be None = no restriction)
    min_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Minimum bedrooms (None = any)
    min_bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # JSON arrays — empty list means "all"
    cities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    property_types: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sources: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<SearchProfile '{self.name}' active={self.is_active}>"