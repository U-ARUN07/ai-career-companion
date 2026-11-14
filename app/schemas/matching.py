"""Schemas for candidate-to-internship matching requests, responses, and explanations."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.resume import CandidateResume


class MatchingExplanation(BaseModel):
    """Detailed RAG / semantic matching explanation."""

    match_reason: str = Field(..., description="Explanation of why the internship was recommended")
    matching_skills: List[str] = Field(default_factory=list, description="Skills present in both candidate and role")
    relevant_projects: List[str] = Field(default_factory=list, description="Candidate projects aligned with the role")
    missing_required_skills: List[str] = Field(
        default_factory=list, description="Required skills not explicitly found in candidate profile"
    )
    recommendation: str = Field(..., description="Actionable recommendation or learning suggestion")
    disclaimer: str = Field(
        default="Similarity score represents semantic vector proximity in embedding space, not a probability or guarantee of job selection.",
        description="Academic disclaimer distinguishing semantic retrieval from hiring decisions",
    )


class InternshipMatch(BaseModel):
    """Single internship match item."""

    internship_id: str
    title: str
    company: str
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    description: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = None
    education_requirements: Optional[List[str]] = None
    experience_requirements: Optional[str] = None
    location: str
    work_mode: str
    duration: Optional[str] = None
    stipend: Optional[str] = None
    explanation: Optional[MatchingExplanation] = None


class MatchRequest(BaseModel):
    """Request payload for finding matching internships."""

    candidate: CandidateResume
    top_k: int = Field(default=5, ge=1, le=50, description="Number of top matches to retrieve (1 to 50)")
    include_explanation: bool = Field(
        default=False, description="Whether to generate grounded RAG / LLM explanations for each match"
    )


class MatchResponse(BaseModel):
    """Response payload containing ranked internship recommendations."""

    candidate_name: str
    total_matches: int
    matches: List[InternshipMatch]
