"""Database CRUD operations for users, tokens, resumes, profiles, and applications."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app import models, security
from app.schemas.auth import StudentProfileCreate


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Find a user by email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> models.User | None:
    """Find a user by UUID primary key."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, full_name: str, email: str, password: str) -> models.User:
    """Hash password and persist a new user record."""
    user = models.User(
        full_name=full_name,
        email=email,
        hashed_password=security.hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def store_refresh_token(db: Session, user_id: uuid.UUID, token: str, expires_at: datetime) -> models.RefreshToken:
    """Store an active refresh token for rotation and revocation."""
    db_token = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_valid_refresh_token(db: Session, token: str) -> models.RefreshToken | None:
    """Return token only if active, unrevoked, and unexpired."""
    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
    if db_token is None or db_token.revoked:
        return None
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    return db_token


def revoke_refresh_token(db: Session, db_token: models.RefreshToken) -> None:
    """Revoke a refresh token on logout or rotation."""
    db_token.revoked = True
    db.commit()


def get_profile_by_user_id(db: Session, user_id: uuid.UUID) -> models.StudentProfile | None:
    """Fetch student profile by user UUID."""
    return db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()


def upsert_student_profile(db: Session, user_id: uuid.UUID, data: StudentProfileCreate) -> models.StudentProfile:
    """Create or update a student's profile."""
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        profile = models.StudentProfile(user_id=user_id, **data.model_dump())
        db.add(profile)
    else:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


def create_resume(
    db: Session,
    user_id: uuid.UUID,
    original_filename: str,
    stored_filename: str,
    file_path: str,
    content_type: str,
    file_size: int,
    parsed_json: str | None = None,
) -> models.Resume:
    """Record an uploaded resume in the database."""
    resume = models.Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=content_type,
        file_size=file_size,
        parsed_json=parsed_json,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resumes_by_user(db: Session, user_id: uuid.UUID) -> list[models.Resume]:
    """Retrieve all resumes uploaded by a specific user."""
    return (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user_id)
        .order_by(models.Resume.uploaded_at.desc())
        .all()
    )


def get_resume_by_id(db: Session, resume_id: uuid.UUID) -> models.Resume | None:
    """Fetch a single resume by UUID."""
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()


def create_application_record(
    db: Session,
    user_id: uuid.UUID,
    internship_id: str,
    internship_title: str,
    company_name: str,
    match_score: float,
    status: str = "Applied",
    cover_letter: str | None = None,
    notes: str | None = None,
) -> models.ApplicationRecord:
    """Persist a new internship application for a user."""
    app_record = models.ApplicationRecord(
        user_id=user_id,
        internship_id=internship_id,
        internship_title=internship_title,
        company_name=company_name,
        match_score=match_score,
        status=status,
        cover_letter=cover_letter,
        notes=notes,
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)
    return app_record


def get_applications_by_user(db: Session, user_id: uuid.UUID) -> list[models.ApplicationRecord]:
    """List all applications submitted by a user."""
    return (
        db.query(models.ApplicationRecord)
        .filter(models.ApplicationRecord.user_id == user_id)
        .order_by(models.ApplicationRecord.applied_at.desc())
        .all()
    )


def update_application_status(
    db: Session,
    app_id: uuid.UUID,
    new_status: str,
    notes: str | None = None,
) -> models.ApplicationRecord | None:
    """Update status (e.g. Under Review, Interview, Offer) of an application."""
    record = db.query(models.ApplicationRecord).filter(models.ApplicationRecord.id == app_id).first()
    if not record:
        return None
    record.status = new_status
    record.updated_at = datetime.now(timezone.utc)
    if notes is not None:
        record.notes = notes
    db.commit()
    db.refresh(record)
    return record
