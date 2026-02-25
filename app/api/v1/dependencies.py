from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    TOKEN_SUBJECT_KEY,
    TOKEN_TYPE_KEY,
    TokenType,
    decode_access_token,
)
from app.models.user import User

bearer_scheme = HTTPBearer()


def _auth_error(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise _auth_error("Invalid or expired token")

    if payload.get(TOKEN_TYPE_KEY) != TokenType.ACCESS:
        raise _auth_error("Invalid token type")
    user_id: str | None = payload.get(TOKEN_SUBJECT_KEY)
    if not user_id:
        raise _auth_error("Invalid token payload")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise _auth_error("User not found or inactive")
    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
