import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.schedule import Schedule
from app.models.slot import Slot

WEEKDAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _parse_time(t: str) -> tuple[int, int]:
    h, m = t.split(":")
    return int(h), int(m)


def _generate_slots_for_day(
    schedule_id: str,
    day: date,
    time_ranges: list[dict],
    duration: int,
    buffer_before: int,
    buffer_after: int,
) -> list[Slot]:
    slots: list[Slot] = []

    for tr in time_ranges:
        start_h, start_m = _parse_time(tr["start"])
        end_h, end_m = _parse_time(tr["end"])

        range_start = datetime(day.year, day.month, day.day, start_h, start_m, tzinfo=timezone.utc)
        range_end = datetime(day.year, day.month, day.day, end_h, end_m, tzinfo=timezone.utc)

        current = range_start
        while True:
            slot_start = current + timedelta(minutes=buffer_before)
            slot_end = slot_start + timedelta(minutes=duration)

            if slot_end > range_end:
                break

            slots.append(
                Slot(
                    id=str(uuid.uuid4()),
                    schedule_id=schedule_id,
                    start_at=slot_start,
                    end_at=slot_end,
                    status="available",
                )
            )
            current = slot_end + timedelta(minutes=buffer_after)

    return slots


async def regenerate_slots(db: AsyncSession, schedule: Schedule) -> None:
    # Delete all future available slots
    await db.execute(
        delete(Slot).where(
            Slot.schedule_id == schedule.id,
            Slot.status == "available",
            Slot.start_at > datetime.now(timezone.utc),
        )
    )

    if not schedule.is_active:
        await db.commit()
        return

    availability: dict = schedule.availability or {}
    today = datetime.now(timezone.utc).date()

    new_slots: list[Slot] = []
    for offset in range(settings.slot_generation_days):
        day = today + timedelta(days=offset)
        weekday_name = WEEKDAY_NAMES[day.weekday()]
        time_ranges = availability.get(weekday_name, [])

        if not time_ranges:
            continue

        new_slots.extend(
            _generate_slots_for_day(
                schedule_id=schedule.id,
                day=day,
                time_ranges=time_ranges,
                duration=schedule.duration,
                buffer_before=schedule.buffer_before,
                buffer_after=schedule.buffer_after,
            )
        )

    db.add_all(new_slots)
    await db.commit()


async def get_available_slots_for_date(
    db: AsyncSession, schedule_id: str, target_date: date
) -> list[Slot]:
    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(Slot).where(
            Slot.schedule_id == schedule_id,
            Slot.status == "available",
            Slot.start_at >= day_start,
            Slot.start_at < day_end,
        ).order_by(Slot.start_at)
    )
    return list(result.scalars().all())
