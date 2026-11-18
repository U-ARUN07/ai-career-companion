"""Resume upload, storage, parsing, and automated vector matching routes."""

import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.database import get_db
from app.models import User
from app.routes.auth_routes import get_optional_current_user, get_current_user
from app.schemas.auth import ResumeOut
from app.schemas.matching import MatchResponse
from app.services.resume_parser import resume_parser
from app.services.matching_service import matching_service

router = APIRouter(prefix="/resume", tags=["Resume Parsing & Management"])

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def get_or_create_demo_user(db: Session) -> User:
    """Helper ensuring a default candidate user (Arun) exists for unauthenticated demo uploads."""
    demo = crud.get_user_by_email(db, "arun.student@example.com")
    if not demo:
        demo = crud.create_user(
            db,
            full_name="Arun",
            email="arun.student@example.com",
            password="DemoPassword123!",
        )
    return demo


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """Upload resume file (.pdf, .docx, .txt), parse structured content, and store on disk & database."""
    if not current_user:
        current_user = get_or_create_demo_user(db)

    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 10 MB limit.")

    # Save to disk under uploads/resumes/<user_id>/<uuid>.<ext>
    user_dir = settings.uploads_dir / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = user_dir / stored_filename
    file_path.write_bytes(contents)

    # Parse resume into structured CandidateResume model
    try:
        raw_text = resume_parser.extract_text(contents, original_name)
        candidate_resume = resume_parser.parse_to_candidate_resume(
            raw_text, default_name=current_user.full_name or "Arun"
        )
        parsed_json_str = candidate_resume.model_dump_json(indent=2)
    except Exception as e:
        parsed_json_str = json.dumps({"parsing_error": str(e)})

    # Persist in DB
    return crud.create_resume(
        db=db,
        user_id=current_user.id,
        original_filename=original_name,
        stored_filename=stored_filename,
        file_path=str(file_path),
        content_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        parsed_json=parsed_json_str,
    )


@router.post("/upload-and-match", response_model=MatchResponse)
async def upload_and_match(
    file: UploadFile = File(...),
    top_k: int = 5,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """End-to-End Pipeline: Upload file -> Parse Skills & Sections -> Semantic RAG Vector Search matches."""
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    candidate_name = current_user.full_name if current_user else "Arun"
    raw_text = resume_parser.extract_text(contents, original_name)
    candidate_resume = resume_parser.parse_to_candidate_resume(raw_text, default_name=candidate_name)

    # Run vector semantic search
    matching_result = matching_service.find_matches(
        candidate_data=candidate_resume,
        top_k=top_k,
    )
    return matching_result


@router.get("/", response_model=list[ResumeOut])
def list_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all resumes uploaded by the logged-in student."""
    return crud.get_resumes_by_user(db, current_user.id)


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download stored resume file ensuring strict ownership security."""
    resume = crud.get_resume_by_id(db, resume_id)
    if resume is None or resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    return FileResponse(
        path=resume.file_path,
        filename=resume.original_filename,
        media_type=resume.content_type,
    )
