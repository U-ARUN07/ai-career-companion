"""Authentication and student profile API routes."""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import crud, security
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    UserCreate,
    UserOut,
    LoginRequest,
    TokenPair,
    RefreshRequest,
    StudentProfileCreate,
    StudentProfileOut,
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Validate Bearer JWT access token and return authenticated User."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error

    try:
        decoded = security.decode_token(token)
    except ValueError:
        raise credentials_error

    if decoded.get("type") != "access":
        raise credentials_error

    try:
        user_id = uuid.UUID(decoded["sub"])
    except (KeyError, ValueError):
        raise credentials_error

    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_error
    return user


def get_optional_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User | None:
    """Return User if token is valid, otherwise return None without raising 401."""
    if not token:
        return None
    try:
        decoded = security.decode_token(token)
        if decoded.get("type") != "access":
            return None
        user_id = uuid.UUID(decoded["sub"])
        return crud.get_user_by_id(db, user_id)
    except Exception:
        return None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new student user."""
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db, payload.full_name, payload.email, payload.password)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate student credentials and issue JWT access and refresh token pair."""
    user = crud.get_user_by_email(db, payload.email)
    if not user or not security.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")

    access_token = security.create_access_token(str(user.id))
    refresh_token = security.create_refresh_token(str(user.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    crud.store_refresh_token(db, user.id, refresh_token, expires_at)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Rotate an unexpired refresh token for a brand-new token pair."""
    try:
        decoded = security.decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    db_token = crud.get_valid_refresh_token(db, payload.refresh_token)
    if db_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

    crud.revoke_refresh_token(db, db_token)

    user_id = decoded["sub"]
    user = crud.get_user_by_id(db, uuid.UUID(user_id))
    access_token = security.create_access_token(user_id)
    new_refresh_token = security.create_refresh_token(user_id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    crud.store_refresh_token(db, db_token.user_id, new_refresh_token, expires_at)

    return TokenPair(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserOut.model_validate(user) if user else None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Revoke refresh token on user logout."""
    db_token = crud.get_valid_refresh_token(db, payload.refresh_token)
    if db_token:
        crud.revoke_refresh_token(db, db_token)
    return None


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get authenticated user details."""
    return current_user


@router.get("/profile", response_model=StudentProfileOut | None)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve current student profile."""
    profile = crud.get_profile_by_user_id(db, current_user.id)
    return profile


@router.put("/profile", response_model=StudentProfileOut)
def update_my_profile(
    payload: StudentProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upsert student profile."""
    return crud.upsert_student_profile(db, current_user.id, payload)
