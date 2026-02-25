from datetime import datetime, timedelta, timezone
from enum import Enum

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


TOKEN_SUBJECT_KEY = "sub"
TOKEN_TYPE_KEY = "type"
TOKEN_EXP_KEY = "exp"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    payload = {
        TOKEN_SUBJECT_KEY: user_id,
        TOKEN_TYPE_KEY: TokenType.ACCESS,
        TOKEN_EXP_KEY: datetime.now(timezone.utc)
        + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


def create_refresh_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    payload = {
        TOKEN_SUBJECT_KEY: user_id,
        TOKEN_TYPE_KEY: TokenType.REFRESH,
        TOKEN_EXP_KEY: datetime.now(timezone.utc)
        + (expires_delta or timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
