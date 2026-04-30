import uuid
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth import (
    create_access_token,
    generate_oauth_state,
    get_or_create_google_user,
    get_user_by_email,
    get_user_by_slug,
    hash_password,
    verify_oauth_state,
    verify_password,
)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, response_model_by_alias=True)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if await get_user_by_slug(db, payload.slug):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already taken")

    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        timezone=payload.timezone,
        slug=payload.slug,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse, response_model_by_alias=True)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    # JWT is stateless — client drops the token
    return None


@router.get("/me", response_model=UserResponse, response_model_by_alias=True)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google")
async def google_login():
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth not configured")

    params = urlencode({
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": generate_oauth_state(),
        "access_type": "online",
    })
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if not verify_oauth_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange code")

        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_resp.json()['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user info")

        userinfo = userinfo_resp.json()

    user = await get_or_create_google_user(
        db,
        google_id=userinfo["sub"],
        email=userinfo["email"],
        name=userinfo.get("name", userinfo["email"]),
    )

    token = create_access_token(user.id)
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?token={token}")
