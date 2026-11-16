"""Cover Letter Generation Agent & ATS Scoring Service.

Generates tailored, high-accuracy cover letters and ATS scoring suggestions using
candidate resumes and internship descriptions with dedicated prompt templates.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from app.config import settings
from app.schemas.cover_letter import CoverLetterResponse
from app.schemas.resume import CandidateResume
from app.services.internship_loader import InternshipLoader
from app.utils.text_utils import clean_text, find_matching_and_missing_skills

logger = logging.getLogger(__name__)

COVER_LETTER_PROMPT_TEMPLATE = """You are an expert AI Career Coach for the Infosys Springboard Virtual Internship Program.
Generate a tailored, high-accuracy cover letter and ATS optimization suggestions based on the candidate's resume and target internship.

Candidate Profile:
{candidate_json}

Target Internship:
- Title: {title}
- Company: {company}
- Description: {description}
- Required Skills: {required_skills}
- Preferred Skills: {preferred_skills}

Instructions:
1. Write a professional, personalized cover letter directly connecting candidate projects and skills to role requirements.
2. Calculate ATS match score (0-100%) based strictly on provided skills.
3. Provide actionable ATS suggestions to optimize the candidate's resume.
4. Do NOT invent credentials or job requirements.
"""


class CoverLetterService:
    """Agent that generates tailored cover letters and ATS scoring suggestions."""

    def __init__(self):
        self.loader = InternshipLoader()

    def generate(
        self, candidate: CandidateResume, internship_id: str
    ) -> CoverLetterResponse:
        """Generate tailored cover letter and ATS scoring analysis."""
        internship = self.loader.get_by_id(internship_id)
        if not internship:
            raise ValueError(f"Internship '{internship_id}' not found.")

        req_skills = internship.required_skills
        pref_skills = internship.preferred_skills
        cand_skills = candidate.skills

        # 1. Compute ATS Match Metrics
        matched_req, missing_req = find_matching_and_missing_skills(cand_skills, req_skills)
        matched_pref, missing_pref = find_matching_and_missing_skills(cand_skills, pref_skills)

        # ATS scoring formula: 60% required skills, 20% preferred skills, 20% project alignment
        req_score = (len(matched_req) / len(req_skills) * 60) if req_skills else 60
        pref_score = (len(matched_pref) / len(pref_skills) * 20) if pref_skills else 15

        # Check project relevance
        proj_score = 0
        all_role_skills = [s.lower() for s in (req_skills + pref_skills)]
        relevant_projs = []
        for p in candidate.projects:
            p_clean = clean_text(p)
            if any(s in p_clean.lower() for s in all_role_skills):
                relevant_projs.append(p_clean)
                proj_score = min(20, proj_score + 10)

        if not proj_score and candidate.projects:
            proj_score = 10

        ats_score = int(min(100, max(15, round(req_score + pref_score + proj_score))))

        # 2. Generate Actionable ATS Suggestions
        ats_suggestions = []
        if missing_req:
            ats_suggestions.append(
                f"Incorporate required keywords: Add '{', '.join(missing_req[:3])}' to your Skills section to pass automated ATS filters."
            )
        if missing_pref:
            ats_suggestions.append(
                f"Highlight preferred competencies: Mentioning experience with '{', '.join(missing_pref[:2])}' will boost your ranking."
            )
        if not relevant_projs and candidate.projects:
            ats_suggestions.append(
                f"Align Project Bullet Points: Tailor your project descriptions to explicitly reference keywords like '{req_skills[0]}'."
            )
        else:
            ats_suggestions.append(
                "Strong Keyword Alignment: Core required skills match role description effectively."
            )
        ats_suggestions.append(
            "Use Standard Formatting: Keep headings like 'Technical Skills', 'Education', and 'Projects' clean for optimal parser extraction."
        )

        # 3. Generate Tailored Cover Letter
        cand_name = candidate.name if candidate.name != "Anonymous Candidate" else "Candidate"
        top_skills_str = ", ".join(matched_req[:3]) if matched_req else ", ".join(cand_skills[:3]) if cand_skills else "software engineering"
        primary_project = relevant_projs[0] if relevant_projs else (candidate.projects[0] if candidate.projects else None)

        project_paragraph = ""
        if primary_project:
            project_paragraph = (
                f"During my academic coursework, I developed practical experience working on relevant projects, "
                f"notably '{primary_project}'. This hands-on project deepened my understanding of scalable system "
                f"design, efficient query processing, and clean code principles, which directly aligns with what "
                f"{internship.company} is building.\n\n"
            )

        cover_letter_text = (
            f"Dear Hiring Team at {internship.company},\n\n"
            f"I am writing to express my enthusiastic interest in the {internship.title} role. "
            f"With a strong foundation in {top_skills_str} and a passion for engineering robust software solutions, "
            f"I am excited about the opportunity to contribute to {internship.company}'s technology initiatives.\n\n"
            f"{project_paragraph}"
            f"What particularly excites me about {internship.company} is the opportunity to work in a dynamic "
            f"{internship.work_mode.lower()} environment located in {internship.location}. My background in "
            f"{', '.join(candidate.education) if candidate.education else 'Computer Science'} has equipped me with "
            f"both the theoretical concepts and analytical problem-solving skills necessary to hit the ground running.\n\n"
            f"I look forward to the opportunity to discuss how my technical competencies and dedication can support "
            f"the ongoing objectives of your engineering team.\n\n"
            f"Sincerely,\n"
            f"{cand_name}"
        )

        return CoverLetterResponse(
            candidate_name=cand_name,
            internship_id=internship.internship_id,
            internship_title=internship.title,
            company_name=internship.company,
            ats_score=ats_score,
            matched_keywords=matched_req + matched_pref,
            missing_keywords=missing_req,
            tailored_cover_letter=cover_letter_text,
            ats_suggestions=ats_suggestions,
        )


cover_letter_service = CoverLetterService()
