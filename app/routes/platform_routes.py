"""Routes for Cover Letter Generation, Application Tracking, and Career Chatbot."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import User
from app.routes.auth_routes import get_optional_current_user
from app.schemas.cover_letter import (
    ApplicationRecord,
    ApplicationSubmissionRequest,
    ChatbotQueryRequest,
    ChatbotQueryResponse,
    CoverLetterRequest,
    CoverLetterResponse,
)
from app.services.application_service import application_service
from app.services.chatbot_service import chatbot_service
from app.services.cover_letter_service import cover_letter_service

router = APIRouter(prefix="/api/v1", tags=["Milestone Extensions"])


class StatusUpdateRequest(BaseModel):
    status: str = Field(description="New status: 'Applied', 'Under Review', 'Interview Scheduled', 'Offer', 'Rejected'")
    notes: Optional[str] = Field(default=None, description="Optional reviewer or student notes")


@router.post(
    "/cover-letter/generate",
    response_model=CoverLetterResponse,
    summary="Generate Tailored Cover Letter & ATS Scoring",
)
def generate_cover_letter(request: CoverLetterRequest):
    """Generate a high-accuracy, personalized cover letter and ATS scoring analysis."""
    try:
        return cover_letter_service.generate(request.candidate, request.internship_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/applications/apply",
    response_model=ApplicationRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Internship Application (Application Tracking Module)",
)
def apply_to_internship(
    request: ApplicationSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Submit an internship application with verified cover letter and recorded timestamp."""
    try:
        record = application_service.submit_application(request)
        # If user is logged in, also record in database
        if current_user:
            try:
                crud.create_application_record(
                    db=db,
                    user_id=current_user.id,
                    internship_id=request.internship_id,
                    internship_title=record.internship_title,
                    company_name=record.company_name,
                    match_score=float(record.ats_score),
                    status=record.status,
                    cover_letter=record.cover_letter,
                    notes=f"Candidate: {request.candidate.name}",
                )
            except Exception:
                pass
        return record
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/applications",
    response_model=List[ApplicationRecord],
    summary="List All Tracked Applications",
)
def get_applications():
    """Retrieve history of student internship applications."""
    return application_service.list_applications()


@router.patch(
    "/applications/{app_id}/status",
    summary="Update Application Tracking Status",
)
def update_application_status(
    app_id: str,
    payload: StatusUpdateRequest,
):
    """Update status (e.g. Applied -> Under Review -> Interview Scheduled -> Offer)."""
    updated = application_service.update_status(app_id, payload.status, payload.notes)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Application '{app_id}' not found.")
    return updated


@router.post(
    "/assistant/chat",
    response_model=ChatbotQueryResponse,
    summary="Conversational Career Assistant (Chatbot with Guardrails)",
)
def chat_with_assistant(request: ChatbotQueryRequest):
    """Query the RAG Career Assistant. Features out-of-scope guardrails and anti-hallucination checks."""
    try:
        return chatbot_service.answer_query(request.message, request.candidate_context)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
