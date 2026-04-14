from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.schedule import ScheduleResponse
from app.schemas.slot import SlotResponse
from app.schemas.user import UserResponse
from app.services.booking import create_booking
from app.services.slot import get_all_slots_for_date, get_dates_with_available_slots

router = APIRouter(prefix="/public", tags=["public"])


class PublicProfileResponse(UserResponse):
    pass


async def _get_host_by_slug(db: AsyncSession, slug: str) -> User:
    result = await db.execute(select(User).where(User.slug == slug))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return user


async def _get_active_schedule(db: AsyncSession, slug: str, schedule_id: str, host_id: str) -> Schedule:
    result = await db.execute(
        select(Schedule).where(
            Schedule.id == schedule_id,
            Schedule.user_id == host_id,
            Schedule.is_active,
        )
    )
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule


@router.get("/{slug}", tags=["public"])
async def get_public_profile(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    host = await _get_host_by_slug(db, slug)

    schedules_result = await db.execute(
        select(Schedule).where(
            Schedule.user_id == host.id,
            Schedule.is_active,
        )
    )
    schedules = list(schedules_result.scalars().all())

    return {
        "user": UserResponse.model_validate(host).model_dump(by_alias=True),
        "schedules": [
            ScheduleResponse.model_validate(s).model_dump(by_alias=True)
            for s in schedules
        ],
    }


@router.get(
    "/{slug}/schedules/{schedule_id}/available-dates",
    response_model=list[str],
)
async def get_schedule_available_dates(
    slug: str,
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return ISO date strings that have at least one available slot in the booking window."""
    host = await _get_host_by_slug(db, slug)
    await _get_active_schedule(db, slug, schedule_id, host.id)

    return await get_dates_with_available_slots(db, schedule_id, host.id)


@router.get(
    "/{slug}/schedules/{schedule_id}/slots",
    response_model=list[SlotResponse],
    response_model_by_alias=True,
)
async def get_all_slots(
    slug: str,
    schedule_id: str,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
):
    """Return all slots for a date (available, booked, blocked) so the UI can render status."""
    host = await _get_host_by_slug(db, slug)
    await _get_active_schedule(db, slug, schedule_id, host.id)

    slots = await get_all_slots_for_date(db, schedule_id, date, host.id)
    return slots


@router.post(
    "/{slug}/schedules/{schedule_id}/bookings",
    response_model=BookingResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_public_booking(
    slug: str,
    schedule_id: str,
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    host = await _get_host_by_slug(db, slug)
    schedule = await _get_active_schedule(db, slug, schedule_id, host.id)

    booking = await create_booking(
        db=db,
        schedule=schedule,
        payload=payload,
        frontend_url=settings.frontend_url,
    )
    return booking
