import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    schedule_id: Mapped[str] = mapped_column(String, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id: Mapped[str] = mapped_column(String, ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True)
    guest_name: Mapped[str] = mapped_column(String, nullable=False)
    guest_email: Mapped[str] = mapped_column(String, nullable=False)
    guest_note: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "confirmed", "cancelled", name="booking_status"),
        nullable=False,
        default="pending",
    )
    confirmation_token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    cancel_token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
