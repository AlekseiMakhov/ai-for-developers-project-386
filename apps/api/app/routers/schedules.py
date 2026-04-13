import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.services.slot import regenerate_slots

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleResponse], response_model_by_alias=True)
async def list_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Schedule).where(Schedule.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=ScheduleResponse, response_model_by_alias=True)
async def create_schedule(
    payload: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = Schedule(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        duration=payload.duration,
        buffer_before=payload.buffer_before,
        buffer_after=payload.buffer_after,
        availability=payload.availability.model_dump(),
        timezone=payload.timezone,
        is_active=payload.is_active,
        color=payload.color,
        slug=payload.slug,
    )
    db.add(schedule)
    await db.flush()
    await regenerate_slots(db, schedule)
    await db.refresh(schedule)
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleResponse, response_model_by_alias=True)
async def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = await _get_own_schedule(db, schedule_id, current_user.id)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse, response_model_by_alias=True)
async def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = await _get_own_schedule(db, schedule_id, current_user.id)

    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "availability":
            setattr(schedule, field, payload.availability.model_dump())
        else:
            setattr(schedule, field, value)

    await regenerate_slots(db, schedule)
    await db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = await _get_own_schedule(db, schedule_id, current_user.id)
    await db.delete(schedule)
    await db.commit()


async def _get_own_schedule(db: AsyncSession, schedule_id: str, user_id: str) -> Schedule:
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule
