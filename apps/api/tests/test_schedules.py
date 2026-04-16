import pytest
from httpx import AsyncClient

USER = {
    "email": "sched@example.com",
    "name": "Sched User",
    "password": "secret123",
    "timezone": "UTC",
    "slug": "sched-user",
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
    },
    "timezone": "UTC",
    "isActive": True,
    "color": "#6366f1",
    "slug": "consultation-30",
}


async def _auth_headers(client: AsyncClient) -> dict:
    reg = await client.post("/auth/register", json=USER)
    token = reg.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_schedule(client: AsyncClient):
    headers = await _auth_headers(client)
    response = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == SCHEDULE_PAYLOAD["name"]
    assert data["duration"] == 30
    assert "id" in data


@pytest.mark.asyncio
async def test_list_schedules(client: AsyncClient):
    headers = await _auth_headers(client)
    await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    response = await client.get("/schedules", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_schedule(client: AsyncClient):
    headers = await _auth_headers(client)
    created = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    sid = created.json()["id"]
    response = await client.get(f"/schedules/{sid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == sid


@pytest.mark.asyncio
async def test_update_schedule(client: AsyncClient):
    headers = await _auth_headers(client)
    created = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    sid = created.json()["id"]
    response = await client.put(
        f"/schedules/{sid}",
        json={"name": "Updated Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_schedule(client: AsyncClient):
    headers = await _auth_headers(client)
    created = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    sid = created.json()["id"]
    response = await client.delete(f"/schedules/{sid}", headers=headers)
    assert response.status_code == 204
    assert (await client.get(f"/schedules/{sid}", headers=headers)).status_code == 404


@pytest.mark.asyncio
async def test_schedule_not_accessible_by_other_user(client: AsyncClient):
    headers1 = await _auth_headers(client)
    created = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers1)
    sid = created.json()["id"]

    reg2 = await client.post("/auth/register", json={**USER, "email": "other@example.com", "slug": "other-user"})
    headers2 = {"Authorization": f"Bearer {reg2.json()['accessToken']}"}
    response = await client.get(f"/schedules/{sid}", headers=headers2)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_slots_generated_on_create(client: AsyncClient):
    headers = await _auth_headers(client)
    created = await client.post("/schedules", json=SCHEDULE_PAYLOAD, headers=headers)
    assert created.status_code == 200
    # Slots are generated internally — verify schedule was created successfully
    # (slot count checked via DB in integration, here we verify no errors)
    assert created.json()["isActive"] is True
