"""LLM service providing intelligent generative capabilities via Groq Cloud.

Powers conversational responses, personalized cover letter enhancements,
grounded matching explanations, dynamic interview question generation,
and mock interview evaluations with instant fallback to rule-based algorithms.
"""

import json
import logging
import re
from typing import Optional, Dict, Any, List

from app.config import settings

logger = logging.getLogger(__name__)


class GroqLLMService:
    """Manages high-speed Groq Cloud API interactions with automatic error recovery."""

    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        if settings.groq_api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=settings.groq_api_key, timeout=12.0)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
                self._client = None

    def is_available(self) -> bool:
        return self._client is not None

    def generate_chat_response(
        self,
        user_message: str,
        retrieved_context: str = "",
        system_instructions: Optional[str] = None,
    ) -> Optional[str]:
        """Generate conversational response using Groq LLM with low latency."""
        if not self.is_available():
            return None

        system = system_instructions or (
            "You are the IntelliIntern AI Career Companion for the Infosys Springboard VIP 7.0 platform. "
            "Help students with internship discovery, matching analysis, resume enhancement, and interview guidance. "
            "Be encouraging, highly structured, concise, and professional. "
            "Use clear Markdown formatting with bullet points and bold headers. "
            "Only answer queries related to internships, technical domains, applications, and career development."
        )

        messages = [{"role": "system", "content": system}]
        if retrieved_context:
            messages.append({
                "role": "system",
                "content": f"Verified Knowledge Base Internships:\n{retrieved_context}\nAnswer the student's question directly based on these opportunities."
            })
        messages.append({"role": "user", "content": user_message})

        try:
            resp = self._client.chat.completions.create(
                messages=messages,
                model=settings.groq_model,
                temperature=0.3,
                max_tokens=500,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else None
        except Exception as e:
            logger.warning(f"Groq chat generation error (fallback will activate): {e}")
            return None

    def generate_cover_letter(
        self,
        candidate_summary: str,
        internship_details: str,
    ) -> Optional[str]:
        """Generate tailored, ATS-compliant cover letter using Groq LLM."""
        if not self.is_available():
            return None

        prompt = (
            f"Candidate Profile:\n{candidate_summary}\n\n"
            f"Target Internship:\n{internship_details}\n\n"
            "Write a highly professional, 3-paragraph tailored cover letter for this candidate applying to the target internship. "
            "Paragraph 1: Clear introductory hook expressing enthusiastic interest in the specific position and company. "
            "Paragraph 2: Deep alignment connecting the candidate's actual projects, coursework, and technical skills to the role's responsibilities. "
            "Paragraph 3: Confident, proactive closing expressing readiness for an interview.\n"
            "Keep the tone articulate, professional, and authentic. Do NOT hallucinate unlisted credentials."
        )

        try:
            resp = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert AI Career Coach generating ATS-optimized, high-conversion cover letters."},
                    {"role": "user", "content": prompt},
                ],
                model=settings.groq_model,
                temperature=0.4,
                max_tokens=600,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else None
        except Exception as e:
            logger.warning(f"Groq cover letter generation error: {e}")
            return None

    def generate_matching_explanation(
        self,
        candidate_context: str,
        internship_details: str,
        similarity_score: float,
    ) -> Optional[Dict[str, Any]]:
        """Generate structured RAG matching explanation in JSON format."""
        if not self.is_available():
            return None

        prompt = (
            f"Candidate Profile:\n{candidate_context}\n\n"
            f"Target Internship:\n{internship_details}\n"
            f"Semantic Similarity Score: {similarity_score:.4f}\n\n"
            "Analyze the candidate's resume against the internship opportunity. Return a valid JSON object with EXACTLY these keys:\n"
            "{\n"
            '  "match_reason": "2-3 sentences explaining why this role was retrieved based on overlapping skills/projects",\n'
            '  "matching_skills": ["list of overlapping skills present in both candidate and role"],\n'
            '  "relevant_projects": ["list of candidate projects relevant to the role"],\n'
            '  "missing_required_skills": ["list of internship required skills that candidate appears to lack"],\n'
            '  "recommendation": "1-2 sentences with actionable guidance for interview prep or upskilling"\n'
            "}\n"
            "Do NOT invent candidate skills. If no skills are missing, return an empty list."
        )

        try:
            resp = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a factual, grounded JSON career matching assistant for the Infosys Springboard VIP 7.0 program. Output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                model=settings.groq_model,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content
            if raw:
                return json.loads(raw.strip())
            return None
        except Exception as e:
            logger.warning(f"Groq matching explanation error: {e}")
            return None

    def generate_interview_questions(
        self,
        internship: Dict[str, Any],
        candidate_skills: List[str],
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate 5 tailored technical & behavioral interview questions in JSON format."""
        if not self.is_available():
            return None

        title = internship.get("title", "Software Engineering Intern")
        company = internship.get("company", "Tech Innovations Inc.")
        domain = internship.get("domain", "Technology")
        req_skills = internship.get("required_skills", [])

        prompt = (
            f"Internship Role: {title} at {company} (Domain: {domain})\n"
            f"Role Required Skills: {', '.join(req_skills)}\n"
            f"Candidate Skills: {', '.join(candidate_skills)}\n\n"
            "Generate exactly 5 tailored interview questions for this specific role and candidate.\n"
            "Return a valid JSON object with key 'questions', which contains an array of 5 objects, each with:\n"
            "- id: string ('q1', 'q2', 'q3', 'q4', 'q5')\n"
            "- category: one of 'Core Technical', 'Domain & Problem Solving', 'System & Algorithmic', 'Behavioral / Collaboration', 'Role Motivation & Company Fit'\n"
            "- question: clear, targeted interview question\n"
            "- topics_tested: array of 2-3 specific technical or behavioral topics tested\n"
            "- interviewer_focus: 1 sentence on what the interviewer evaluates in the answer\n"
            "- recommended_approach: 2-3 bullet lines describing how the candidate should structure their answer (e.g. STAR method, architecture, trade-offs)\n"
        )

        try:
            resp = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer and hiring committee lead. Output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                model=settings.groq_model,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=900,
            )
            raw = resp.choices[0].message.content
            if raw:
                data = json.loads(raw.strip())
                questions = data.get("questions", [])
                if len(questions) == 5:
                    return questions
            return None
        except Exception as e:
            logger.warning(f"Groq interview questions generation error: {e}")
            return None

    def evaluate_interview_answer(
        self,
        question: str,
        answer: str,
        category: str = "Technical",
    ) -> Optional[Dict[str, Any]]:
        """Evaluate candidate's mock practice answer using Groq LLM."""
        if not self.is_available():
            return None

        prompt = (
            f"Interview Question ({category}):\n{question}\n\n"
            f"Candidate Answer:\n{answer}\n\n"
            "Perform a rigorous, fair evaluation of this candidate's mock practice response.\n"
            "Return a valid JSON object with:\n"
            "- score: integer from 0 to 100\n"
            "- verdict: short phrase (e.g. 'Exceptional Response', 'Solid Answer', 'Needs More Detail', etc.)\n"
            "- feedback: 2-3 sentences of constructive, actionable feedback\n"
            "- strengths: list of 1-2 specific strengths in the response\n"
            "- areas_for_improvement: list of 1-2 actionable recommendations\n"
            "- star_framework_applied: boolean indicating whether Situation, Task, Action, Result / outcome was demonstrated"
        )

        try:
            resp = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a senior technical hiring manager evaluating mock candidate answers. Output valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                model=settings.groq_model,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=450,
            )
            raw = resp.choices[0].message.content
            if raw:
                data = json.loads(raw.strip())
                data["word_count"] = len(answer.strip().split())
                return data
            return None
        except Exception as e:
            logger.warning(f"Groq interview evaluation error: {e}")
            return None


llm_service = GroqLLMService()
