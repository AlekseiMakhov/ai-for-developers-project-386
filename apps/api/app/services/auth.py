import hashlib
import hmac
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str:
    """Returns user_id or raises JWTError."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise JWTError("Missing subject")
    return user_id


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_slug(db: AsyncSession, slug: str) -> User | None:
    result = await db.execute(select(User).where(User.slug == slug))
    return result.scalar_one_or_none()


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> User | None:
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def get_or_create_google_user(
    db: AsyncSession, google_id: str, email: str, name: str
) -> User:
    user = await get_user_by_google_id(db, google_id)
    if user:
        return user

    user = await get_user_by_email(db, email)
    if user:
        user.google_id = google_id
        await db.commit()
        await db.refresh(user)
        return user

    slug = await _unique_slug(db, email.split("@")[0])
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        hashed_password=None,
        google_id=google_id,
        slug=slug,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "-", base.lower())
    candidate = slug
    i = 1
    while await get_user_by_slug(db, candidate):
        candidate = f"{slug}-{i}"
        i += 1
    return candidate


def generate_oauth_state() -> str:
    token = secrets.token_urlsafe(32)
    sig = hmac.new(settings.secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()
    return f"{token}.{sig}"


def verify_oauth_state(state: str) -> bool:
    try:
        token, sig = state.rsplit(".", 1)
        expected = hmac.new(settings.secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False
