from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.models.slot import Slot
from app.models.user import User
from app.schemas.booking import BookingResponse
from app.services.booking import cancel_booking, confirm_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse], response_model_by_alias=True)
async def list_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get all schedule IDs owned by user
    sched_result = await db.execute(
        select(Schedule.id).where(Schedule.user_id == current_user.id)
    )
    schedule_ids = [row[0] for row in sched_result.all()]

    if not schedule_ids:
        return []

    result = await db.execute(
        select(
            Booking.id,
            Booking.schedule_id,
            Booking.slot_id,
            Booking.guest_name,
            Booking.guest_email,
            Booking.guest_note,
            Booking.status,
            Booking.confirmation_token,
            Booking.cancel_token,
            Booking.created_at,
            Slot.start_at.label("slot_start_at"),
            Slot.end_at.label("slot_end_at"),
            Schedule.name.label("schedule_name"),
        )
        .join(Slot, Slot.id == Booking.slot_id)
        .join(Schedule, Schedule.id == Booking.schedule_id)
        .where(Booking.schedule_id.in_(schedule_ids))
        .order_by(Booking.created_at.desc())
    )
    return [BookingResponse.model_validate(dict(row)) for row in result.mappings().all()]


@router.get("/confirm/{token}", response_model=BookingResponse, response_model_by_alias=True)
async def guest_confirm_booking(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return await confirm_booking(db, token)


@router.get("/cancel/{token}", response_model=BookingResponse, response_model_by_alias=True)
async def guest_cancel_booking(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return await cancel_booking(db, token)


@router.get("/{booking_id}", response_model=BookingResponse, response_model_by_alias=True)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Booking.id,
            Booking.schedule_id,
            Booking.slot_id,
            Booking.guest_name,
            Booking.guest_email,
            Booking.guest_note,
            Booking.status,
            Booking.confirmation_token,
            Booking.cancel_token,
            Booking.created_at,
            Slot.start_at.label("slot_start_at"),
            Slot.end_at.label("slot_end_at"),
            Schedule.name.label("schedule_name"),
        )
        .join(Slot, Slot.id == Booking.slot_id)
        .join(Schedule, Schedule.id == Booking.schedule_id)
        .where(Booking.id == booking_id, Schedule.user_id == current_user.id)
    )
    row = result.mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return BookingResponse.model_validate(dict(row))


@router.patch("/{booking_id}/confirm", response_model=BookingResponse, response_model_by_alias=True)
async def host_confirm_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    booking = await _get_own_booking(db, booking_id, current_user.id)
    return await confirm_booking(db, booking.confirmation_token)


@router.patch("/{booking_id}/cancel", response_model=BookingResponse, response_model_by_alias=True)
async def host_cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    booking = await _get_own_booking(db, booking_id, current_user.id)
    return await cancel_booking(db, booking.cancel_token)


async def _get_own_booking(db: AsyncSession, booking_id: str, user_id: str) -> Booking:
    result = await db.execute(
        select(Booking)
        .join(Schedule, Schedule.id == Booking.schedule_id)
        .where(Booking.id == booking_id, Schedule.user_id == user_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking
