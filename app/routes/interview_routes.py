"""Interview Preparation and Question Generation Agent routes."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.interview_service import interview_service
from app.services.internship_loader import internship_loader

router = APIRouter(prefix="/api/v1/interview", tags=["Interview Prep Agent"])


class InterviewQuestionsRequest(BaseModel):
    internship_id: str = Field(description="ID of target internship")
    candidate_skills: List[str] = Field(default_factory=list, description="List of candidate skills")


class InterviewEvaluationRequest(BaseModel):
    question: str = Field(description="Interview question prompt")
    answer: str = Field(description="Candidate's practice response")
    category: str = Field(default="Technical", description="Question category")


@router.post("/questions", summary="Generate Tailored Interview Questions")
def generate_interview_questions(payload: InterviewQuestionsRequest):
    """Generate 5 tailored technical, domain, algorithmic, behavioral, and motivation questions."""
    internship = internship_loader.get_by_id(payload.internship_id)
    if not internship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Internship '{payload.internship_id}' not found.",
        )

    internship_dict = internship.model_dump()
    questions = interview_service.generate_interview_questions(
        internship=internship_dict,
        candidate_skills=payload.candidate_skills,
    )

    return {
        "internship_id": payload.internship_id,
        "internship_title": internship.title,
        "company": internship.company,
        "questions": questions,
    }


@router.post("/evaluate", summary="Evaluate Candidate Practice Answer")
def evaluate_practice_answer(payload: InterviewEvaluationRequest):
    """Evaluate candidate's mock practice answer against industry scoring rubric."""
    evaluation = interview_service.evaluate_response(
        question=payload.question,
        answer=payload.answer,
        category=payload.category,
    )
    return evaluation
