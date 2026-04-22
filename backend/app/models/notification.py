"""
models/notification.py — Notification history model
"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("search_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # email | sms
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="email")

    # sent | failed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="sent")

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Notification {self.channel} listing={self.listing_id} profile={self.profile_id}>"