import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import Resume
from app.utils.auth import get_current_user
from app.utils.security import hash_password

router = APIRouter(
    prefix="/api/profile",
    tags=["Student Profile"]
)


class ProfileUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    phone: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: Optional[str] = None
    target_role: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=current_user.id,
            university="University / Higher Education Institution",
            degree="Bachelor of Technology / Engineering / Sciences",
            graduation_year="2026",
            target_role="Career & Technical Intern",
            bio="Motivated student applying multidisciplinary engineering principles to impactful real-world projects.",
            location="Open to Remote / Hybrid",
            skills=json.dumps(["Core Domain Knowledge", "Problem Solving", "Analytical Thinking", "Project Execution"])
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    skills_list = []
    if profile.skills:
        try:
            skills_list = json.loads(profile.skills)
        except Exception:
            skills_list = [s.strip() for s in profile.skills.split(",") if s.strip()]

    # Find active resume
    active_resume = db.query(Resume).filter(
        Resume.owner_id == current_user.id,
        Resume.is_active == True
    ).order_by(Resume.id.desc()).first()

    if not active_resume:
        active_resume = db.query(Resume).filter(
            Resume.owner_id == current_user.id
        ).order_by(Resume.id.desc()).first()

    return {
        "id": profile.id,
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "phone": profile.phone or "",
        "university": profile.university or "",
        "degree": profile.degree or "",
        "graduation_year": profile.graduation_year or "",
        "target_role": profile.target_role or "Software Engineer Intern",
        "bio": profile.bio or "",
        "location": profile.location or "",
        "github_url": profile.github_url or "",
        "linkedin_url": profile.linkedin_url or "",
        "portfolio_url": profile.portfolio_url or "",
        "skills": skills_list,
        "active_resume_id": active_resume.id if active_resume else None,
        "active_resume_filename": active_resume.filename if active_resume else None
    }


@router.put("/me")
def update_my_profile(
    data: ProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Update User basic credentials (Name, Email)
    if data.name is not None and data.name.strip():
        current_user.name = data.name.strip()

    if data.email is not None and data.email.strip():
        clean_email = data.email.strip().lower()
        if clean_email != current_user.email:
            existing = db.query(User).filter(User.email == clean_email, User.id != current_user.id).first()
            if existing:
                raise HTTPException(status_code=400, detail="This email is already registered to another account.")
            current_user.email = clean_email

    # 2. Update Password if specified
    if data.password:
        if data.password != data.confirm_password:
            raise HTTPException(status_code=400, detail="New password and confirm password do not match.")
        if len(data.password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")
        current_user.password = hash_password(data.password)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    if data.phone is not None:
        profile.phone = data.phone
    if data.university is not None:
        profile.university = data.university
    if data.degree is not None:
        profile.degree = data.degree
    if data.graduation_year is not None:
        profile.graduation_year = data.graduation_year
    if data.target_role is not None:
        profile.target_role = data.target_role
    if data.bio is not None:
        profile.bio = data.bio
    if data.location is not None:
        profile.location = data.location
    if data.github_url is not None:
        profile.github_url = data.github_url
    if data.linkedin_url is not None:
        profile.linkedin_url = data.linkedin_url
    if data.portfolio_url is not None:
        profile.portfolio_url = data.portfolio_url
    if data.skills is not None:
        profile.skills = json.dumps(data.skills)

    db.commit()
    db.refresh(current_user)
    db.refresh(profile)

    # Master Bidirectional Synchronization across User, StudentProfile, active Resume JSON, on-disk PDF, and Match Cache
    try:
        from app.services.profile_sync import sync_from_profile_manual
        sync_payload = data.dict(exclude_unset=True)
        if data.name:
            sync_payload["name"] = data.name
        if data.email:
            sync_payload["email"] = data.email
        sync_from_profile_manual(current_user.id, sync_payload, db)
    except Exception as sync_err:
        print("Master profile sync error on manual update:", sync_err)

    return {
        "message": "Profile and account credentials updated successfully across all modules! ✅",
        "name": current_user.name,
        "email": current_user.email,
        "target_role": profile.target_role,
        "university": profile.university,
        "location": profile.location
    }
