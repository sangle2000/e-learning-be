from datetime import datetime, timezone, timedelta
from typing import Any, Union, Optional
import jwt
import bcrypt
from app.core.config import settings

import uuid

ALGORITHM = "HS256"


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JWT access token with an expiration time.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "jti": uuid.uuid4().hex
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JWT refresh token with an expiration time.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default refresh token expiry is 7 days (1 week)
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": uuid.uuid4().hex
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed bcrypt password.
    """
    # Truncate plain_password to 72 bytes to avoid ValueError from bcrypt >= 5.0.0,
    # and to ensure compatibility with older bcrypt versions that did silent truncation.
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    # Truncate password to 72 bytes to avoid ValueError from bcrypt >= 5.0.0.
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")
