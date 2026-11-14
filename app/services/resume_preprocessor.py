"""Resume preprocessing pipeline.

Converts structured candidate resume data into clean, normalized text suitable
for semantic embedding generation and FAISS vector retrieval.
"""

from typing import Any, Dict, Union
from app.schemas.resume import CandidateResume
from app.utils.text_utils import clean_string_list, clean_text


class ResumePreprocessor:
    """Preprocesses and normalizes candidate resumes into rich embedding text."""

    @staticmethod
    def parse_input(candidate_data: Union[CandidateResume, Dict[str, Any]]) -> CandidateResume:
        """Parse raw dictionary or validate existing CandidateResume schema safely."""
        if isinstance(candidate_data, CandidateResume):
            return candidate_data
        if isinstance(candidate_data, dict):
            return CandidateResume(**candidate_data)
        # Fallback if invalid type passed
        return CandidateResume()

    @classmethod
    def preprocess_to_text(cls, candidate_data: Union[CandidateResume, Dict[str, Any]]) -> str:
        """Convert a structured candidate resume into a unified textual representation.

        Sections are formatted with clear semantic markers so the embedding model
        captures technical skills, projects, domain interests, and credentials.
        """
        resume = cls.parse_input(candidate_data)

        sections = []

        # 1. Candidate Name & Summary
        name = clean_text(resume.name)
        summary = clean_text(resume.summary)

        intro_parts = []
        if name and name != "Anonymous Candidate":
            intro_parts.append(f"Candidate Profile: {name}")
        if summary:
            intro_parts.append(f"Professional Summary: {summary}")
        if intro_parts:
            sections.append(". ".join(intro_parts))

        # 2. Key Technical & Soft Skills
        skills = clean_string_list(resume.skills)
        if skills:
            sections.append(f"Technical and Core Skills: {', '.join(skills)}")

        # 3. Projects (heavily weighted for semantic matching)
        projects = clean_string_list(resume.projects)
        if projects:
            sections.append(f"Key Projects: {'; '.join(projects)}")

        # 4. Education
        education = clean_string_list(resume.education)
        if education:
            sections.append(f"Education: {', '.join(education)}")

        # 5. Experience
        experience = clean_string_list(resume.experience)
        if experience:
            sections.append(f"Experience: {'; '.join(experience)}")

        # 6. Certifications & Achievements
        certifications = clean_string_list(resume.certifications)
        achievements = clean_string_list(resume.achievements)
        cred_parts = []
        if certifications:
            cred_parts.append(f"Certifications: {', '.join(certifications)}")
        if achievements:
            cred_parts.append(f"Achievements: {', '.join(achievements)}")
        if cred_parts:
            sections.append(". ".join(cred_parts))

        # Handle empty resume edge case
        if not sections:
            return "Entry-level candidate seeking student internship opportunities."

        full_representation = ". ".join(sections)
        if not full_representation.endswith("."):
            full_representation += "."

        return full_representation
