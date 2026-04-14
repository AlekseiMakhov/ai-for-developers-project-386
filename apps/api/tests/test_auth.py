import pytest
from httpx import AsyncClient

USER_PAYLOAD = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "secret123",
    "timezone": "UTC",
    "slug": "test-user",
}


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/auth/register", json=USER_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/auth/register", json=USER_PAYLOAD)
    response = await client.post("/auth/register", json=USER_PAYLOAD)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_duplicate_slug(client: AsyncClient):
    await client.post("/auth/register", json=USER_PAYLOAD)
    payload = {**USER_PAYLOAD, "email": "other@example.com"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/auth/register", json=USER_PAYLOAD)
    response = await client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    assert "accessToken" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json=USER_PAYLOAD)
    response = await client.post(
        "/auth/login",
        json={"email": USER_PAYLOAD["email"], "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    reg = await client.post("/auth/register", json=USER_PAYLOAD)
    token = reg.json()["accessToken"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["slug"] == USER_PAYLOAD["slug"]


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.post("/auth/logout")
    assert response.status_code == 204
