"""Internship data models and validation schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Internship(BaseModel):
    """Schema representing an internship opportunity.

    Note: All opportunities in this system are synthetic and designed for
    academic semantic matching simulations for the Infosys Springboard VIP 7.0 program.
    """

    internship_id: str = Field(..., description="Unique internship identifier, e.g., INT001")
    title: str = Field(..., description="Job/internship title")
    company: str = Field(..., description="Hosting organization / synthetic company name")
    description: str = Field(..., description="Detailed role description and responsibilities")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory technical or domain skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Desirable or nice-to-have skills")
    education_requirements: List[str] = Field(default_factory=list, description="Target degrees or streams")
    experience_requirements: str = Field(default="Freshers or students", description="Expected background or experience")
    location: str = Field(..., description="City or primary work location")
    work_mode: str = Field(..., description="Remote, Hybrid, or On-site")
    duration: str = Field(..., description="Internship period, e.g., 3 months, 6 months")
    stipend: str = Field(..., description="Monthly compensation or unpaid note")
    is_synthetic: bool = Field(default=True, description="Flag indicating synthetic educational data")

    @field_validator("required_skills", "preferred_skills", "education_requirements", mode="before")
    @classmethod
    def sanitize_skills_and_edu(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]
        cleaned = []
        for item in v:
            if item is not None:
                item_str = str(item).strip()
                if item_str:
                    cleaned.append(item_str)
        return cleaned

    @field_validator("title", "company", "description", "location", "work_mode", "duration", "stipend", mode="before")
    @classmethod
    def sanitize_text(cls, v):
        if v is None:
            return ""
        return str(v).strip()
