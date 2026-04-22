"""
models/listing.py — Listing database model
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    city: Mapped[str] = mapped_column(String(200), nullable=False, default="", index=True)
    region: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False, default="")

    price: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size_sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # house | condo | duplex | land | other
    property_type: Mapped[str] = mapped_column(String(50), nullable=False, default="other", index=True)

    listing_url: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    images: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # MD5 hash of address+city+price+bedrooms — used for cross-source dedup
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Listing {self.source}:{self.external_id} {self.address} ${self.price:,}>"