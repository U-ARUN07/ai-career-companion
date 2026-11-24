import re
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

import string
SPECIAL_CHARACTERS = set(string.punctuation)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(hours=2)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return token


def create_password_reset_token(email: str, expires_minutes: int = 30) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": email,
        "purpose": "password_reset",
        "exp": expire
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_password_reset_token(token: str) -> str:
    """Verifies the reset token and returns the email if valid, or raises ValueError."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("purpose") != "password_reset":
            raise ValueError("Invalid token purpose")
        email: str = payload.get("sub")
        if not email:
            raise ValueError("Missing email in token")
        return email
    except Exception as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def validate_password_criteria(password: str, email: str = None) -> None:
    """
    Validates password criteria with user-friendly priority.
    Allows flexible user choice while ensuring non-empty password.
    """
    if not password or len(password.strip()) == 0:
        raise ValueError("Password is required.")

    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters long.")

    return None
