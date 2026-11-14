"""Resume data models and validation schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CandidateResume(BaseModel):
    """Structured candidate resume extracted from resume parsing.

    Safely handles missing or null fields, converts them to clean defaults,
    and supports rich student profiles.
    """

    name: str = Field(default="Anonymous Candidate", description="Full name of candidate")
    summary: Optional[str] = Field(default="", description="Professional / career summary")
    skills: List[str] = Field(default_factory=list, description="Extracted technical and soft skills")
    education: List[str] = Field(default_factory=list, description="Degrees, colleges, and academic programs")
    experience: List[str] = Field(default_factory=list, description="Prior work, internships, or role experience")
    projects: List[str] = Field(default_factory=list, description="Academic or personal projects")
    certifications: List[str] = Field(default_factory=list, description="Professional or course certifications")
    achievements: List[str] = Field(default_factory=list, description="Competitions, awards, or hackathon achievements")

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if not v or not isinstance(v, str):
            return "Anonymous Candidate"
        clean = v.strip()
        return clean if clean else "Anonymous Candidate"

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v):
        if v is None:
            return ""
        return str(v).strip()

    @field_validator("skills", "education", "experience", "projects", "certifications", "achievements", mode="before")
    @classmethod
    def sanitize_list_fields(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # If passed as a single string, wrap or split if comma-separated
            v = [v]
        if not isinstance(v, (list, tuple, set)):
            return [str(v)]
        cleaned = []
        for item in v:
            if item is not None:
                item_str = str(item).strip()
                if item_str:
                    cleaned.append(item_str)
        return cleaned
