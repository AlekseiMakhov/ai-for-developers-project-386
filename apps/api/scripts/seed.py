"""Seed script: creates default John Doe user + two sample schedules with slots."""

import asyncio
import sys
import uuid

from sqlalchemy import select

sys.path.insert(0, "/app")

from app.database import AsyncSessionLocal
from app.models.schedule import Schedule
from app.models.user import User
from app.services.auth import hash_password
from app.services.slot import regenerate_slots

DEFAULT_AVAILABILITY = {
    "monday": [{"start": "09:00", "end": "18:00"}],
    "tuesday": [{"start": "09:00", "end": "18:00"}],
    "wednesday": [{"start": "09:00", "end": "18:00"}],
    "thursday": [{"start": "09:00", "end": "18:00"}],
    "friday": [{"start": "09:00", "end": "18:00"}],
}


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # Check if default user already exists
        result = await db.execute(select(User).where(User.email == "john@example.com"))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                id=str(uuid.uuid4()),
                email="john@example.com",
                name="John Doe",
                hashed_password=hash_password("changeme"),
                timezone="Europe/Moscow",
                slug="john",
            )
            db.add(user)
            await db.flush()
            print(f"Created user: {user.email} (slug={user.slug})")
        else:
            print(f"User already exists: {user.email}")

        # Check if schedules already exist
        sched_result = await db.execute(
            select(Schedule).where(Schedule.user_id == user.id)
        )
        existing = list(sched_result.scalars().all())
        if existing:
            print(f"Schedules already exist ({len(existing)}), skipping schedule seed")
            await db.commit()
            return

        schedules = [
            Schedule(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name="Консультация 30 мин",
                description="Краткая консультация",
                duration=30,
                buffer_before=0,
                buffer_after=5,
                availability=DEFAULT_AVAILABILITY,
                timezone="Europe/Moscow",
                is_active=True,
                slug="consultation-30",
            ),
            Schedule(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name="Встреча 60 мин",
                description="Полноценная встреча",
                duration=60,
                buffer_before=0,
                buffer_after=10,
                availability=DEFAULT_AVAILABILITY,
                timezone="Europe/Moscow",
                is_active=True,
                slug="meeting-60",
            ),
        ]

        for s in schedules:
            db.add(s)
        await db.flush()
        print(f"Created {len(schedules)} schedules")

        # Generate slots for each schedule
        for s in schedules:
            await regenerate_slots(db, s)
            print(f"  Slots generated for: {s.name}")

        await db.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
