from datetime import date, timedelta

import pytest
from httpx import AsyncClient

HOST = {
    "email": "bhost@example.com",
    "name": "Booking Host",
    "password": "secret123",
    "timezone": "UTC",
    "slug": "booking-host",
}

SCHEDULE_PAYLOAD = {
    "name": "Консультация",
    "duration": 30,
    "bufferBefore": 0,
    "bufferAfter": 0,
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
    "slug": "consult",
}


async def _setup(client: AsyncClient):
    reg = await client.post("/auth/register", json=HOST)
    token = reg.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    sched = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    schedule_id = sched.json()["id"]

    target = date.today() + timedelta(days=1)
    slots = (
        await client.get(
            f"/public/{HOST['slug']}/schedules/{schedule_id}/slots",
            params={"date": target.isoformat()},
        )
    ).json()
    slot_id = slots[0]["id"]

    booking = (
        await client.post(
            f"/public/{HOST['slug']}/schedules/{schedule_id}/bookings",
            json={"slotId": slot_id, "guestName": "Guest", "guestEmail": "guest@example.com"},
        )
    ).json()

    return headers, booking


@pytest.mark.asyncio
async def test_list_bookings(client: AsyncClient):
    headers, _ = await _setup(client)
    response = await client.get("/bookings", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_booking(client: AsyncClient):
    headers, booking = await _setup(client)
    response = await client.get(f"/bookings/{booking['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == booking["id"]


@pytest.mark.asyncio
async def test_host_confirm_booking(client: AsyncClient):
    headers, booking = await _setup(client)
    response = await client.patch(f"/bookings/{booking['id']}/confirm", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_host_cancel_booking(client: AsyncClient):
    headers, booking = await _setup(client)
    response = await client.patch(f"/bookings/{booking['id']}/cancel", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_bookings_not_accessible_by_other_user(client: AsyncClient):
    headers, booking = await _setup(client)

    other_reg = await client.post(
        "/auth/register",
        json={**HOST, "email": "other2@example.com", "slug": "other2-user"},
    )
    other_headers = {"Authorization": f"Bearer {other_reg.json()['accessToken']}"}

    response = await client.get(f"/bookings/{booking['id']}", headers=other_headers)
    assert response.status_code == 404
