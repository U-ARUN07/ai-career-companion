"""Explanation service for grounded RAG-based matching rationales.

Generates structured explanations linking candidate qualifications to internship requirements.
Operates fully offline via intelligent grounded rule templates and supports optional
Google Gemini or OpenAI API integration when configured.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from app.config import settings
from app.schemas.matching import MatchingExplanation
from app.schemas.resume import CandidateResume
from app.utils.text_utils import clean_text, find_matching_and_missing_skills
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

# Grounded RAG Prompt Template
RAG_EXPLANATION_PROMPT = """You are a Career Matching Assistant for Infosys Springboard Virtual Internship Program.
Analyze the candidate's resume and the retrieved internship opportunity below.
Generate an honest, grounded evaluation.

STRICT INSTRUCTIONS:
1. Grounding: Rely ONLY on the explicitly provided Candidate Profile and Internship Details.
2. Anti-Hallucination: Do NOT invent candidate skills, projects, experience, or company details.
3. Non-Guarantee: Never claim the candidate is guaranteed to be selected or hired. The similarity score represents vector closeness in embedding space.
4. Missing Info: If required information is not found in the candidate profile, clearly list it as missing.

Candidate Profile:
{candidate_context}

Retrieved Internship:
- ID: {internship_id}
- Title: {title}
- Company: {company}
- Description: {description}
- Required Skills: {required_skills}
- Preferred Skills: {preferred_skills}
- Semantic Similarity Score: {similarity_score:.4f}

Provide your evaluation in valid JSON with these keys:
{{
  "match_reason": "string explaining why this role was retrieved based on overlapping skills/projects",
  "matching_skills": ["list of overlapping skills"],
  "relevant_projects": ["list of candidate projects relevant to the role"],
  "missing_required_skills": ["list of internship required skills candidate appears to lack"],
  "recommendation": "string recommending specific preparation, projects, or next steps"
}}
"""


class ExplanationService:
    """Generates structured, grounded explanations for candidate-internship matches."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.explanation_provider

    def generate_explanation(
        self,
        candidate: CandidateResume,
        internship: Dict[str, Any],
        similarity_score: float,
    ) -> MatchingExplanation:
        """Generate a grounded explanation using configured provider or rule-based fallback."""
        if (self.provider == "groq" or settings.explanation_provider == "groq") and llm_service.is_available():
            try:
                candidate_str = json.dumps(candidate.model_dump(), indent=2)
                internship_str = (
                    f"ID: {internship.get('internship_id')}\n"
                    f"Title: {internship.get('title')}\n"
                    f"Company: {internship.get('company')}\n"
                    f"Description: {internship.get('description')}\n"
                    f"Required Skills: {', '.join(internship.get('required_skills', []))}\n"
                    f"Preferred Skills: {', '.join(internship.get('preferred_skills', []))}"
                )
                groq_exp = llm_service.generate_matching_explanation(
                    candidate_context=candidate_str,
                    internship_details=internship_str,
                    similarity_score=similarity_score,
                )
                if groq_exp:
                    return MatchingExplanation(**groq_exp)
            except Exception as e:
                logger.warning(f"Groq API explanation failed ({e}); falling back to grounded rule engine.")

        if self.provider == "gemini" and settings.gemini_api_key:
            try:
                return self._generate_gemini_explanation(candidate, internship, similarity_score)
            except Exception as e:
                logger.warning(f"Gemini API explanation failed ({e}); falling back to grounded rule engine.")

        if self.provider == "openai" and settings.openai_api_key:
            try:
                return self._generate_openai_explanation(candidate, internship, similarity_score)
            except Exception as e:
                logger.warning(f"OpenAI API explanation failed ({e}); falling back to grounded rule engine.")

        # Default free, fully offline grounded rule-based explanation
        return self._generate_rule_based_explanation(candidate, internship, similarity_score)

    def _generate_rule_based_explanation(
        self,
        candidate: CandidateResume,
        internship: Dict[str, Any],
        similarity_score: float,
    ) -> MatchingExplanation:
        """Grounded, deterministic explanation generator.

        Extracts exact skill overlaps, matches projects by keyword similarity,
        identifies missing skills, and provides realistic career guidance without hallucination.
        """
        req_skills = internship.get("required_skills", [])
        pref_skills = internship.get("preferred_skills", [])
        title = internship.get("title", "Internship Opportunity")
        company = internship.get("company", "Organization")

        # 1. Matching & Missing Skills
        matching_skills, missing_skills = find_matching_and_missing_skills(
            candidate.skills, req_skills
        )

        # Also check preferred skills overlap
        pref_matched, _ = find_matching_and_missing_skills(candidate.skills, pref_skills)

        # 2. Find Relevant Projects
        relevant_projects: List[str] = []
        all_role_skills_lower = {s.lower() for s in (req_skills + pref_skills)}

        for proj in candidate.projects:
            proj_clean = clean_text(proj)
            if not proj_clean:
                continue
            proj_lower = proj_clean.lower()
            # If project mentions any role skills or words from title
            if any(skill in proj_lower for skill in all_role_skills_lower) or any(
                w.lower() in proj_lower for w in title.split() if len(w) > 3
            ):
                relevant_projects.append(proj_clean)

        if not relevant_projects and candidate.projects:
            # If no direct skill matched, check if general tech keywords match
            relevant_projects.append(f"General technical experience: {candidate.projects[0]}")

        # 3. Match Reason
        if matching_skills:
            match_reason = (
                f"Candidate's background demonstrates strong alignment with {title} at {company}. "
                f"Demonstrated proficiency in {', '.join(matching_skills[:3])} directly supports "
                f"the primary responsibilities outlined in the role."
            )
        else:
            match_reason = (
                f"Semantic vector search identified high conceptual overlap with {title} at {company} "
                f"based on candidate's technical profile, academic background, and project interests."
            )

        # 4. Actionable Recommendation
        if missing_skills:
            recommendation = (
                f"To strengthen candidacy for this role, prioritize developing hands-on competency in "
                f"{', '.join(missing_skills[:2])}. Building a dedicated portfolio project highlighting "
                f"these skills will bridge the gap."
            )
        elif pref_skills and not pref_matched:
            recommendation = (
                f"Candidate satisfies core requirements. Exploring preferred technologies such as "
                f"{', '.join(pref_skills[:2])} can provide a competitive edge."
            )
        else:
            recommendation = (
                "Excellent alignment on core prerequisites. Highlight relevant project architecture "
                "and API design decisions in your interview discussions."
            )

        return MatchingExplanation(
            match_reason=match_reason,
            matching_skills=matching_skills,
            relevant_projects=relevant_projects,
            missing_required_skills=missing_skills,
            recommendation=recommendation,
        )

    def _generate_gemini_explanation(
        self,
        candidate: CandidateResume,
        internship: Dict[str, Any],
        similarity_score: float,
    ) -> MatchingExplanation:
        """Call Google Gemini API if user has configured GEMINI_API_KEY."""
        import httpx

        prompt = RAG_EXPLANATION_PROMPT.format(
            candidate_context=json.dumps(candidate.model_dump(), indent=2),
            internship_id=internship.get("internship_id", ""),
            title=internship.get("title", ""),
            company=internship.get("company", ""),
            description=internship.get("description", ""),
            required_skills=", ".join(internship.get("required_skills", [])),
            preferred_skills=", ".join(internship.get("preferred_skills", [])),
            similarity_score=similarity_score,
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_text)
            return MatchingExplanation(**parsed)

    def _generate_openai_explanation(
        self,
        candidate: CandidateResume,
        internship: Dict[str, Any],
        similarity_score: float,
    ) -> MatchingExplanation:
        """Call OpenAI API if user has configured OPENAI_API_KEY."""
        import httpx

        prompt = RAG_EXPLANATION_PROMPT.format(
            candidate_context=json.dumps(candidate.model_dump(), indent=2),
            internship_id=internship.get("internship_id", ""),
            title=internship.get("title", ""),
            company=internship.get("company", ""),
            description=internship.get("description", ""),
            required_skills=", ".join(internship.get("required_skills", [])),
            preferred_skills=", ".join(internship.get("preferred_skills", [])),
            similarity_score=similarity_score,
        )

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a factual, grounded JSON career matching assistant."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        with httpx.Client(timeout=10.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_text)
            return MatchingExplanation(**parsed)


# Global singleton instance
explanation_service = ExplanationService()
