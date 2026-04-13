import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    buffer_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    buffer_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    availability: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    timezone: Mapped[str] = mapped_column(String, nullable=False, default="UTC")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
