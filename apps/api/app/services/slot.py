import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.booking import Booking
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


async def get_all_slots_for_date(
    db: AsyncSession,
    schedule_id: str,
    target_date: date,
    host_user_id: str | None = None,
) -> list[Slot]:
    """Return all slots (any status) for a given date, ordered by start time.

    When host_user_id is supplied, "available" slots that overlap with any
    pending/confirmed booking on another host schedule are returned as "blocked".
    The change is in-memory only — nothing is persisted.
    """
    day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    result = await db.execute(
        select(Slot).where(
            Slot.schedule_id == schedule_id,
            Slot.start_at >= day_start,
            Slot.start_at < day_end,
        ).order_by(Slot.start_at)
    )
    slots = list(result.scalars().all())

    if not host_user_id or not slots:
        return slots

    # Fetch time ranges of booked slots from OTHER host schedules that touch this day.
    booked_result = await db.execute(
        select(Slot.start_at, Slot.end_at)
        .join(Booking, Booking.slot_id == Slot.id)
        .join(Schedule, Schedule.id == Booking.schedule_id)
        .where(
            Schedule.user_id == host_user_id,
            Booking.status.in_(["pending", "confirmed"]),
            Slot.schedule_id != schedule_id,
            Slot.end_at > day_start,
            Slot.start_at < day_end,
        )
    )
    booked_ranges = booked_result.all()

    if not booked_ranges:
        return slots

    # Mark available slots blocked if they overlap any cross-schedule booking.
    # This is an in-memory mutation — no db.commit() is called in GET handlers.
    for slot in slots:
        if slot.status != "available":
            continue
        for booked_start, booked_end in booked_ranges:
            if slot.start_at < booked_end and slot.end_at > booked_start:
                slot.status = "blocked"
                break

    return slots


async def get_dates_with_available_slots(
    db: AsyncSession,
    schedule_id: str,
    host_user_id: str | None = None,
) -> list[str]:
    """Return sorted list of ISO date strings that have at least one effectively
    available slot within the booking window.

    When host_user_id is supplied, a slot is considered available only if it
    does not overlap with any pending/confirmed booking on another host schedule.
    """
    today = datetime.now(timezone.utc).date()
    from_dt = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    to_dt = from_dt + timedelta(days=settings.slot_generation_days)

    # Subquery: booked slot rows from OTHER schedules of the same host
    # that overlap s.start_at / s.end_at (correlated on the outer Slot alias s).
    if host_user_id:
        booked_slot = Slot.__table__.alias("booked_slot")
        conflict_subq = (
            select(booked_slot.c.id)
            .join(Booking.__table__, Booking.slot_id == booked_slot.c.id)
            .join(Schedule.__table__, Schedule.id == Booking.schedule_id)
            .where(
                Schedule.user_id == host_user_id,
                Booking.status.in_(["pending", "confirmed"]),
                booked_slot.c.schedule_id != schedule_id,
                booked_slot.c.start_at < Slot.end_at,
                booked_slot.c.end_at > Slot.start_at,
            )
            .correlate(Slot)
            .exists()
        )
        query = select(Slot.start_at).where(
            Slot.schedule_id == schedule_id,
            Slot.status == "available",
            Slot.start_at >= from_dt,
            Slot.start_at < to_dt,
            not_(conflict_subq),
        )
    else:
        query = select(Slot.start_at).where(
            Slot.schedule_id == schedule_id,
            Slot.status == "available",
            Slot.start_at >= from_dt,
            Slot.start_at < to_dt,
        )

    result = await db.execute(query)
    dates: set[str] = set()
    for start_at in result.scalars().all():
        dates.add(start_at.date().isoformat())
    return sorted(dates)
