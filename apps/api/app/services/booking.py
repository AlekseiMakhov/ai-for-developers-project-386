import uuid
from datetime import timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.schedule import Schedule
from app.models.slot import Slot
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.services import email as email_service


def _fmt_slot(slot: Slot) -> str:
    return slot.start_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")


async def create_booking(
    db: AsyncSession,
    schedule: Schedule,
    payload: BookingCreate,
    frontend_url: str,
) -> Booking:
    # Verify slot belongs to schedule and is available
    result = await db.execute(
        select(Slot).where(
            Slot.id == payload.slot_id,
            Slot.schedule_id == schedule.id,
            Slot.status == "available",
        )
    )
    slot = result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot not available",
        )

    confirmation_token = str(uuid.uuid4())
    cancel_token = str(uuid.uuid4())

    booking = Booking(
        id=str(uuid.uuid4()),
        schedule_id=schedule.id,
        slot_id=slot.id,
        guest_name=payload.guest_name,
        guest_email=str(payload.guest_email),
        guest_note=payload.guest_note,
        status="pending",
        confirmation_token=confirmation_token,
        cancel_token=cancel_token,
    )
    db.add(booking)

    # Mark slot as booked
    slot.status = "booked"

    await db.commit()
    await db.refresh(booking)

    # Fetch host user for email
    host_result = await db.execute(select(User).where(User.id == schedule.user_id))
    host = host_result.scalar_one_or_none()

    confirmation_link = f"{frontend_url}/bookings/confirm/{confirmation_token}"
    cancel_link = f"{frontend_url}/bookings/cancel/{cancel_token}"

    email_service.send_booking_confirmation(
        guest_email=booking.guest_email,
        guest_name=booking.guest_name,
        schedule_name=schedule.name,
        slot_start=_fmt_slot(slot),
        confirmation_link=confirmation_link,
        cancel_link=cancel_link,
    )

    return booking


async def confirm_booking(db: AsyncSession, confirmation_token: str) -> Booking:
    result = await db.execute(
        select(Booking).where(Booking.confirmation_token == confirmation_token)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already cancelled")

    if booking.status == "confirmed":
        return booking

    booking.status = "confirmed"
    await db.commit()
    await db.refresh(booking)

    # Notify host
    schedule_result = await db.execute(select(Schedule).where(Schedule.id == booking.schedule_id))
    schedule = schedule_result.scalar_one_or_none()

    slot_result = await db.execute(select(Slot).where(Slot.id == booking.slot_id))
    slot = slot_result.scalar_one_or_none()

    if schedule and slot:
        host_result = await db.execute(select(User).where(User.id == schedule.user_id))
        host = host_result.scalar_one_or_none()
        if host:
            email_service.send_booking_confirmed_to_host(
                host_email=host.email,
                host_name=host.name,
                guest_name=booking.guest_name,
                guest_email=booking.guest_email,
                schedule_name=schedule.name,
                slot_start=_fmt_slot(slot),
            )

    return booking


async def cancel_booking(db: AsyncSession, cancel_token: str) -> Booking:
    result = await db.execute(
        select(Booking).where(Booking.cancel_token == cancel_token)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status == "cancelled":
        return booking

    # Free the slot
    slot_result = await db.execute(select(Slot).where(Slot.id == booking.slot_id))
    slot = slot_result.scalar_one_or_none()
    if slot:
        slot.status = "available"

    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)

    # Notify host and guest
    schedule_result = await db.execute(select(Schedule).where(Schedule.id == booking.schedule_id))
    schedule = schedule_result.scalar_one_or_none()

    if schedule and slot:
        host_result = await db.execute(select(User).where(User.id == schedule.user_id))
        host = host_result.scalar_one_or_none()
        if host:
            email_service.send_booking_cancelled(
                to_email=host.email,
                to_name=host.name,
                guest_name=booking.guest_name,
                schedule_name=schedule.name,
                slot_start=_fmt_slot(slot),
            )

    return booking
