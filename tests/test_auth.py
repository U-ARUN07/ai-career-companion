"""Tests for Authentication and Student Profile operations."""

import uuid
from app.database import SessionLocal, init_db
from app import crud, security
from app.routes.auth_routes import register, login, refresh, get_my_profile, update_my_profile
from app.schemas.auth import UserCreate, LoginRequest, RefreshRequest, StudentProfileCreate


def test_auth_and_profile_flow():
    init_db()
    db = SessionLocal()
    try:
        unique_email = f"student_{uuid.uuid4().hex[:6]}@example.com"
        password = "SecurePassword123!"

        # 1. Register User
        reg_payload = UserCreate(full_name="Arun", email=unique_email, password=password)
        user = register(reg_payload, db=db)
        assert user.full_name == "Arun"
        assert user.email == unique_email
        assert user.is_active is True

        # 2. Login User
        login_payload = LoginRequest(email=unique_email, password=password)
        token_pair = login(login_payload, db=db)
        assert token_pair.access_token
        assert token_pair.refresh_token
        assert token_pair.token_type == "bearer"

        # 3. Verify Token Decoding
        decoded = security.decode_token(token_pair.access_token)
        assert decoded["sub"] == str(user.id)
        assert decoded["type"] == "access"

        # 4. Refresh Token Rotation
        ref_payload = RefreshRequest(refresh_token=token_pair.refresh_token)
        new_token_pair = refresh(ref_payload, db=db)
        assert new_token_pair.access_token
        assert new_token_pair.refresh_token != token_pair.refresh_token

        # 5. Upsert and Retrieve Student Profile
        prof_payload = StudentProfileCreate(
            college="Infosys Springboard Institute",
            branch="Computer Science & AI",
            graduation_year=2026,
            skills="Python, FastAPI, FAISS, PyTorch, RAG",
            target_roles="AI/ML Engineer Intern",
        )
        db_user = crud.get_user_by_id(db, user.id)
        updated_profile = update_my_profile(prof_payload, current_user=db_user, db=db)
        assert updated_profile.college == "Infosys Springboard Institute"
        assert updated_profile.graduation_year == 2026

        fetched_profile = get_my_profile(current_user=db_user, db=db)
        assert fetched_profile is not None
        assert fetched_profile.target_roles == "AI/ML Engineer Intern"
    finally:
        db.close()
