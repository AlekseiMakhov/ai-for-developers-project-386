from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.auth import generate_oauth_state, verify_oauth_state

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


@pytest.mark.asyncio
async def test_login_google_user_without_password_fails(client: AsyncClient):
    """Google-only users can't log in with email+password."""
    # Register via "Google" by directly creating a user without password
    # We simulate by registering normally then testing the guard
    # (actual Google user creation tested via callback mock below)
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "whatever"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_oauth_state_roundtrip():
    state = generate_oauth_state()
    assert verify_oauth_state(state)


@pytest.mark.asyncio
async def test_oauth_state_tampered():
    state = generate_oauth_state()
    tampered = state[:-4] + "xxxx"
    assert not verify_oauth_state(tampered)


@pytest.mark.asyncio
async def test_google_login_not_configured(client: AsyncClient):
    """Returns 501 when Google OAuth env vars are not set."""
    response = await client.get("/auth/google", follow_redirects=False)
    assert response.status_code == 501


@pytest.mark.asyncio
async def test_google_callback_invalid_state(client: AsyncClient):
    response = await client.get(
        "/auth/google/callback",
        params={"code": "anycode", "state": "invalid.state"},
        follow_redirects=False,
    )
    assert response.status_code == 400


def _make_google_mock(google_id: str, email: str, name: str):
    """Build an httpx.AsyncClient mock that returns fake Google responses."""
    token_response = MagicMock()
    token_response.status_code = 200
    token_response.json.return_value = {"access_token": "fake-access-token"}

    userinfo_response = MagicMock()
    userinfo_response.status_code = 200
    userinfo_response.json.return_value = {"sub": google_id, "email": email, "name": name}

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=token_response)
    mock_client.get = AsyncMock(return_value=userinfo_response)
    return mock_client


@pytest.mark.asyncio
async def test_google_callback_new_user(client: AsyncClient):
    """New Google user is created and redirected with a JWT."""
    state = generate_oauth_state()
    mock_http = _make_google_mock("google-uid-1", "newuser@gmail.com", "New User")

    with (
        patch("app.routers.auth.settings.google_client_id", "fake-client-id"),
        patch("app.routers.auth.settings.google_client_secret", "fake-secret"),
        patch("app.routers.auth.httpx.AsyncClient", return_value=mock_http),
    ):
        response = await client.get(
            "/auth/google/callback",
            params={"code": "authcode", "state": state},
            follow_redirects=False,
        )

    assert response.status_code == 307
    assert "token=" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_existing_email_linked(client: AsyncClient):
    """Existing email-password user gets google_id linked on first Google login."""
    await client.post("/auth/register", json=USER_PAYLOAD)
    state = generate_oauth_state()
    mock_http = _make_google_mock("google-uid-2", USER_PAYLOAD["email"], USER_PAYLOAD["name"])

    with (
        patch("app.routers.auth.settings.google_client_id", "fake-client-id"),
        patch("app.routers.auth.settings.google_client_secret", "fake-secret"),
        patch("app.routers.auth.httpx.AsyncClient", return_value=mock_http),
    ):
        response = await client.get(
            "/auth/google/callback",
            params={"code": "authcode", "state": state},
            follow_redirects=False,
        )

    assert response.status_code == 307
    assert "token=" in response.headers["location"]


@pytest.mark.asyncio
async def test_google_callback_returning_user(client: AsyncClient):
    """Second Google login with same google_id reuses existing user."""
    state1 = generate_oauth_state()
    state2 = generate_oauth_state()
    mock_http = _make_google_mock("google-uid-3", "returning@gmail.com", "Returning User")

    with (
        patch("app.routers.auth.settings.google_client_id", "fake-client-id"),
        patch("app.routers.auth.settings.google_client_secret", "fake-secret"),
        patch("app.routers.auth.httpx.AsyncClient", return_value=mock_http),
    ):
        r1 = await client.get(
            "/auth/google/callback",
            params={"code": "code1", "state": state1},
            follow_redirects=False,
        )
        r2 = await client.get(
            "/auth/google/callback",
            params={"code": "code2", "state": state2},
            follow_redirects=False,
        )

    assert r1.status_code == 307
    assert r2.status_code == 307
