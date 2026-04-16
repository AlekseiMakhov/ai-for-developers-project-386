from datetime import date, timedelta

import pytest
from httpx import AsyncClient

HOST = {
    "email": "host@example.com",
    "name": "Host User",
    "password": "secret123",
    "timezone": "UTC",
    "slug": "host-user",
}

SCHEDULE_PAYLOAD = {
    "name": "Консультация 30 мин",
    "description": "Быстрая консультация",
    "duration": 30,
    "availability": {
        "monday": [{"start": "09:00", "end": "17:00"}],
        "tuesday": [{"start": "09:00", "end": "17:00"}],
        "wednesday": [{"start": "09:00", "end": "17:00"}],
        "thursday": [{"start": "09:00", "end": "17:00"}],
        "friday": [{"start": "09:00", "end": "17:00"}],
        "saturday": [{"start": "09:00", "end": "17:00"}],
        "sunday": [{"start": "09:00", "end": "17:00"}],
    },
    "timezone": "UTC",
    "isActive": True,
    "color": "#6366f1",
    "slug": "consultation-30",
}


async def _setup(client: AsyncClient) -> tuple[str, str, str]:
    """Register host, create schedule, return (token, slug, schedule_id)."""
    reg = await client.post("/auth/register", json=HOST)
    token = reg.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    sched = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    schedule_id = sched.json()["id"]
    return token, HOST["slug"], schedule_id


@pytest.mark.asyncio
async def test_get_public_profile(client: AsyncClient):
    _, slug, _ = await _setup(client)
    response = await client.get(f"/public/{slug}")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["slug"] == slug
    assert len(data["schedules"]) == 1


@pytest.mark.asyncio
async def test_get_public_profile_not_found(client: AsyncClient):
    response = await client.get("/public/nonexistent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_available_slots(client: AsyncClient):
    _, slug, schedule_id = await _setup(client)
    # Find a valid upcoming weekday with slots
    target = date.today() + timedelta(days=1)
    response = await client.get(
        f"/public/{slug}/schedules/{schedule_id}/slots",
        params={"date": target.isoformat()},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_slots_inactive_schedule(client: AsyncClient):
    token, slug, schedule_id = await _setup(client)
    headers = {"Authorization": f"Bearer {token}"}
    await client.put(f"/schedules/{schedule_id}", json={"isActive": False}, headers=headers)

    target = date.today() + timedelta(days=1)
    response = await client.get(
        f"/public/{slug}/schedules/{schedule_id}/slots",
        params={"date": target.isoformat()},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient):
    _, slug, schedule_id = await _setup(client)

    # Find a day with slots
    target = date.today() + timedelta(days=1)
    slots_resp = await client.get(
        f"/public/{slug}/schedules/{schedule_id}/slots",
        params={"date": target.isoformat()},
    )
    slots = slots_resp.json()
    assert len(slots) > 0

    slot_id = slots[0]["id"]
    payload = {
        "slotId": slot_id,
        "guestName": "Ivan Petrov",
        "guestEmail": "ivan@example.com",
        "guestNote": "Test note",
    }
    response = await client.post(
        f"/public/{slug}/schedules/{schedule_id}/bookings",
        json=payload,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["guestName"] == "Ivan Petrov"
    assert data["status"] == "pending"
    assert "confirmationToken" in data
    assert "cancelToken" in data


@pytest.mark.asyncio
async def test_create_booking_unavailable_slot(client: AsyncClient):
    _, slug, schedule_id = await _setup(client)

    target = date.today() + timedelta(days=1)
    slots_resp = await client.get(
        f"/public/{slug}/schedules/{schedule_id}/slots",
        params={"date": target.isoformat()},
    )
    slots = slots_resp.json()
    slot_id = slots[0]["id"]

    payload = {
        "slotId": slot_id,
        "guestName": "Ivan Petrov",
        "guestEmail": "ivan@example.com",
    }

    # First booking succeeds
    r1 = await client.post(f"/public/{slug}/schedules/{schedule_id}/bookings", json=payload)
    assert r1.status_code == 201

    # Second booking on same slot fails
    r2 = await client.post(
        f"/public/{slug}/schedules/{schedule_id}/bookings",
        json={**payload, "guestEmail": "other@example.com"},
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_guest_confirm_booking(client: AsyncClient):
    _, slug, schedule_id = await _setup(client)

    target = date.today() + timedelta(days=1)
    slots = (
        await client.get(
            f"/public/{slug}/schedules/{schedule_id}/slots",
            params={"date": target.isoformat()},
        )
    ).json()
    slot_id = slots[0]["id"]

    booking = (
        await client.post(
            f"/public/{slug}/schedules/{schedule_id}/bookings",
            json={"slotId": slot_id, "guestName": "Anna", "guestEmail": "anna@example.com"},
        )
    ).json()

    token = booking["confirmationToken"]
    confirm_resp = await client.get(f"/bookings/confirm/{token}")
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_guest_cancel_booking(client: AsyncClient):
    _, slug, schedule_id = await _setup(client)

    target = date.today() + timedelta(days=1)
    slots = (
        await client.get(
            f"/public/{slug}/schedules/{schedule_id}/slots",
            params={"date": target.isoformat()},
        )
    ).json()
    slot_id = slots[0]["id"]

    booking = (
        await client.post(
            f"/public/{slug}/schedules/{schedule_id}/bookings",
            json={"slotId": slot_id, "guestName": "Anna", "guestEmail": "anna@example.com"},
        )
    ).json()

    cancel_token = booking["cancelToken"]
    cancel_resp = await client.get(f"/bookings/cancel/{cancel_token}")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # Slot should be available again
    slots_after = (
        await client.get(
            f"/public/{slug}/schedules/{schedule_id}/slots",
            params={"date": target.isoformat()},
        )
    ).json()
    slot_ids_after = [s["id"] for s in slots_after]
    assert slot_id in slot_ids_after
