import os
import json
import re
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import Resume
from app.models.analysis import ResumeAnalysis
from app.services.cv_generator import generate_cv_pdf_bytes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _clear_matching_cache():
    try:
        from app.routers.matching import _MATCH_CACHE
        _MATCH_CACHE.clear()
    except Exception:
        pass


def sync_from_resume_extraction(user_id: int, extracted_data: Dict[str, Any], resume_id: Optional[int], db: Session) -> Dict[str, Any]:
    """
    Called when a resume is uploaded, seeded, or re-extracted.
    IMPORTANT: The registered User and StudentProfile represent the student's personal account identity
    created at sign-up. Uploading a resume MUST NOT overwrite the candidate's account name, contact info,
    degree, university, or profile details. The extracted resume data belongs strictly to the Resume entity
    and is consumed independently by the ATS Parser, RAG Matching Radar, Skill Gap, and CV Builder modules.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        profile = StudentProfile(user_id=user_id)
        db.add(profile)

    # Extract skills for physical resume PDF generation if needed
    skills_raw = extracted_data.get("skills") or {}
    all_skills = []
    if isinstance(skills_raw, dict):
        all_skills = (skills_raw.get("technical_skills") or []) + (skills_raw.get("tools_frameworks") or [])
    elif isinstance(skills_raw, list):
        all_skills = skills_raw

    clean_skills = [str(s).strip() for s in all_skills if str(s).strip()]

    # Update Physical PDF strictly for the uploaded resume without touching student's user profile
    if resume_id:
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == user_id).first()
        if resume:
            cv_payload = {
                "fullName": user.name or "Arun",
                "roleTitle": profile.target_role or "Software Engineer Intern",
                "email": user.email,
                "phone": profile.phone or "+91 98765 43210",
                "location": profile.location or "Bengaluru, India",
                "linkedin": profile.linkedin_url or "https://linkedin.com",
                "github": profile.github_url or "https://github.com",
                "summary": extracted_data.get("summary") or profile.bio or "Motivated software engineer.",
                "skills": extracted_data.get("skills") or {"technical_skills": clean_skills},
                "experience": extracted_data.get("experience") or [],
                "education": extracted_data.get("education") or [],
                "projects": extracted_data.get("projects") or [],
                "certifications": extracted_data.get("certifications") or []
            }
            try:
                pdf_bytes = generate_cv_pdf_bytes(cv_payload, template="modern")
                pdf_filename = f"{user_id}_{resume_id}_resume.pdf"
                pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                resume.file_path = pdf_path
            except Exception as e:
                print(f"Error generating PDF on resume sync: {e}")

    _clear_matching_cache()
    db.commit()

    return {
        "user_name": user.name,
        "user_email": user.email,
        "target_role": profile.target_role,
        "university": profile.university,
        "skills_count": len(clean_skills)
    }


def sync_from_profile_manual(user_id: int, profile_update: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Called when a student manually edits their profile or credentials in ProfilePage.
    Syncs across User, StudentProfile, active Resume JSON, re-renders the physical PDF,
    and clears matching cache.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if not profile:
        profile = StudentProfile(user_id=user_id)
        db.add(profile)

    # 1. User attributes
    if "name" in profile_update and profile_update["name"]:
        user.name = str(profile_update["name"]).strip()
    if "email" in profile_update and profile_update["email"]:
        user.email = str(profile_update["email"]).strip().lower()

    # 2. StudentProfile attributes
    field_map = [
        ("phone", "phone"),
        ("university", "university"),
        ("degree", "degree"),
        ("graduation_year", "graduation_year"),
        ("target_role", "target_role"),
        ("bio", "bio"),
        ("location", "location"),
        ("github_url", "github_url"),
        ("linkedin_url", "linkedin_url"),
        ("portfolio_url", "portfolio_url"),
    ]
    for key, attr in field_map:
        if key in profile_update and profile_update[key] is not None:
            setattr(profile, attr, str(profile_update[key]).strip())

    if "skills" in profile_update and profile_update["skills"] is not None:
        sk = profile_update["skills"]
        if isinstance(sk, list):
            profile.skills = json.dumps(sk)
        elif isinstance(sk, str):
            profile.skills = json.dumps([s.strip() for s in sk.split(",") if s.strip()])

    # 3. Synchronize active resume
    active_resume = db.query(Resume).filter(
        Resume.owner_id == user_id,
        Resume.is_active == True
    ).order_by(Resume.id.desc()).first()

    if not active_resume:
        active_resume = db.query(Resume).filter(
            Resume.owner_id == user_id
        ).order_by(Resume.id.desc()).first()

    if active_resume:
        res_data = {}
        if active_resume.parsed_data:
            try:
                res_data = json.loads(active_resume.parsed_data)
            except Exception:
                res_data = {}

        p_info = res_data.get("personal_info") or {}
        p_info["name"] = user.name
        p_info["email"] = user.email
        if profile.phone:
            p_info["phone"] = profile.phone
        if profile.location:
            p_info["location"] = profile.location
        if profile.linkedin_url:
            p_info["linkedin"] = profile.linkedin_url
        if profile.github_url:
            p_info["github"] = profile.github_url
        if profile.portfolio_url:
            p_info["portfolio"] = profile.portfolio_url
        res_data["personal_info"] = p_info

        if profile.bio:
            res_data["summary"] = profile.bio
        if profile.target_role:
            res_data["career_recommendation"] = profile.target_role

        # Update education in resume JSON if university/degree updated
        if profile.university or profile.degree:
            edu_list = res_data.get("education") or []
            first_edu = edu_list[0] if (edu_list and isinstance(edu_list[0], dict)) else {}
            if profile.university:
                first_edu["institution"] = profile.university
                first_edu["school"] = profile.university
            if profile.degree:
                first_edu["degree"] = profile.degree
            if profile.graduation_year:
                first_edu["year"] = profile.graduation_year
                first_edu["duration"] = f"Class of {profile.graduation_year}"
            res_data["education"] = [first_edu] + edu_list[1:]

        # Update skills in resume JSON
        if profile.skills:
            try:
                sk_list = json.loads(profile.skills)
                cur_skills = res_data.get("skills") or {}
                if isinstance(cur_skills, dict):
                    cur_skills["technical_skills"] = sk_list
                    res_data["skills"] = cur_skills
                else:
                    res_data["skills"] = {"technical_skills": sk_list}
            except Exception:
                pass

        active_resume.parsed_data = json.dumps(res_data)

        # Re-generate physical PDF with latest updated data
        try:
            cv_payload = {
                "fullName": user.name,
                "roleTitle": profile.target_role or "Full-Stack AI Engineer Intern",
                "email": user.email,
                "phone": profile.phone or "+91 98765 43210",
                "location": profile.location or "Bengaluru, India",
                "linkedin": profile.linkedin_url or "https://linkedin.com",
                "github": profile.github_url or "https://github.com",
                "summary": profile.bio or res_data.get("summary") or "Motivated engineer.",
                "skills": res_data.get("skills") or {"technical_skills": [s.strip() for s in (profile.skills or "").split(",") if s.strip()]},
                "experience": res_data.get("experience") or [],
                "education": res_data.get("education") or [],
                "projects": res_data.get("projects") or [],
                "certifications": res_data.get("certifications") or []
            }
            pdf_bytes = generate_cv_pdf_bytes(cv_payload, template="modern")
            pdf_filename = f"{user_id}_{active_resume.id}_resume.pdf"
            pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            active_resume.file_path = pdf_path
        except Exception as e:
            print(f"Error re-generating physical PDF on profile update: {e}")

    _clear_matching_cache()
    db.commit()
    db.refresh(user)
    db.refresh(profile)

    return {
        "user_name": user.name,
        "user_email": user.email,
        "target_role": profile.target_role,
        "university": profile.university,
        "location": profile.location
    }


def sync_from_cv_builder(user_id: int, cv_payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Called when a student customizes or saves their full CV in CustomizerPage.
    Synchronizes the edited CV into active Resume and regenerates disk PDF,
    WITHOUT overwriting the student's permanent account profile credentials.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}

    # Synchronize strictly into active resume
    active_resume = db.query(Resume).filter(
        Resume.owner_id == user_id,
        Resume.is_active == True
    ).order_by(Resume.id.desc()).first()

    if not active_resume:
        active_resume = db.query(Resume).filter(
            Resume.owner_id == user_id
        ).order_by(Resume.id.desc()).first()

    if active_resume:
        active_resume.parsed_data = json.dumps(cv_payload)
        try:
            template = cv_payload.get("template", "modern")
            pdf_bytes = generate_cv_pdf_bytes(cv_payload, template=template)
            pdf_filename = f"{user_id}_{active_resume.id}_resume.pdf"
            pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            active_resume.file_path = pdf_path
        except Exception as e:
            print(f"Error writing PDF on CV builder sync: {e}")

    _clear_matching_cache()
    db.commit()
    db.refresh(user)

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    return {
        "message": "CV synchronized successfully across the platform! 🎉",
        "user_name": user.name,
        "user_email": user.email,
        "target_role": profile.target_role if profile else "Software Engineer Intern",
        "university": profile.university if profile else "Engineering University"
    }
