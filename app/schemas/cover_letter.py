"""Schemas for Cover Letter Generation and Application Tracking."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.resume import CandidateResume


class CoverLetterRequest(BaseModel):
    """Request payload for generating a tailored cover letter."""

    candidate: CandidateResume
    internship_id: str = Field(..., description="Target internship ID (e.g. INT001)")


class CoverLetterResponse(BaseModel):
    """Generated tailored cover letter with ATS scoring metrics."""

    candidate_name: str
    internship_id: str
    internship_title: str
    company_name: str
    ats_score: int = Field(..., ge=0, le=100, description="ATS match compatibility percentage (0-100)")
    matched_keywords: List[str]
    missing_keywords: List[str]
    tailored_cover_letter: str
    ats_suggestions: List[str]
    disclaimer: str = (
        "ATS score and cover letter are generated for academic demonstration under the "
        "Infosys Springboard VIP 7.0 framework. They do not constitute a hiring guarantee."
    )


class ApplicationSubmissionRequest(BaseModel):
    """Payload to record an internship application in the tracking module."""

    candidate: CandidateResume
    internship_id: str
    cover_letter: str


class ApplicationRecord(BaseModel):
    """Stored record of a submitted internship application."""

    application_id: str
    internship_id: str
    internship_title: str
    company_name: str
    candidate_name: str
    submitted_at: str
    status: str = "Submitted"
    ats_score: int
    cover_letter: str


class ChatbotQueryRequest(BaseModel):
    """Request query for the Conversational Career Assistant."""

    message: str = Field(..., min_length=1, description="User's query")
    candidate_context: Optional[CandidateResume] = None


class ChatbotQueryResponse(BaseModel):
    """Response from the Conversational Career Assistant with guardrail status."""

    reply: str
    is_out_of_scope: bool = False
    retrieved_internships: List[Dict[str, Any]] = []
    guardrail_triggered: bool = False
