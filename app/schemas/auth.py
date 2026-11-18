"""Pydantic schemas for authentication, token rotation, and student profiles."""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    """Payload for POST /api/v1/auth/register."""

    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    """Public user response object."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login."""

    email: EmailStr
    password: str


class TokenPair(BaseModel):
    """JWT Access and Refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut | None = None


class RefreshRequest(BaseModel):
    """Payload for token refresh or logout."""

    refresh_token: str


class StudentProfileCreate(BaseModel):
    """Payload for creating or updating a student profile."""

    college: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    bio: str | None = None
    skills: str | None = None
    target_roles: str | None = None


class StudentProfileOut(StudentProfileCreate):
    """Public student profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID


class ResumeOut(BaseModel):
    """Public uploaded resume metadata response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    content_type: str
    file_size: int
    uploaded_at: datetime
    parsed_json: str | None = None
