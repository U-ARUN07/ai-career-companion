"""Routes for Cover Letter Generation, Application Tracking, and Career Chatbot."""

from typing import List
from fastapi import APIRouter, HTTPException, status
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
def apply_to_internship(request: ApplicationSubmissionRequest):
    """Submit an internship application with verified cover letter and recorded timestamp."""
    try:
        return application_service.submit_application(request)
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
