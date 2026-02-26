from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    TOKEN_EXP_KEY,
    TOKEN_SUBJECT_KEY,
    TOKEN_TYPE_KEY,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models import RefreshToken
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


class EmailAlreadyExistsError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise EmailAlreadyExistsError("Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_tokens(db: AsyncSession, user: User) -> TokenResponse:
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    # Decode to get expiration
    payload = decode_access_token(refresh)

    # Store refresh token in DB
    db_token = RefreshToken(
        token=refresh,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(payload[TOKEN_EXP_KEY], tz=timezone.utc),
    )
    db.add(db_token)
    await db.flush()

    return TokenResponse(access_token=access, refresh_token=refresh)


async def refresh_token(db: AsyncSession, token: str) -> TokenResponse:
    # Decode and validate
    payload = decode_access_token(token)
    if not payload or payload.get(TOKEN_TYPE_KEY) != "refresh":
        raise InvalidRefreshTokenError("Invalid refresh token")

    # Check DB
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),
        )
    )

    db_token = result.scalar_one_or_none()
    if not db_token:
        raise InvalidRefreshTokenError("Refresh token not found or revoked")

    # Check expiry
    if db_token.expires_at < datetime.now(timezone.utc):
        raise InvalidRefreshTokenError("Refresh token expired")

    # Revoke old token (rotation)
    db_token.is_revoked = True

    # Get user
    user_id = payload.get(TOKEN_SUBJECT_KEY)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise InvalidRefreshTokenError("User not found")

    # Issue new tokens
    return await create_tokens(db, user)


async def logout_user(db: AsyncSession, token: str) -> None:
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.is_revoked = True


async def logout_all(db: AsyncSession, user_id) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.is_revoked = True
