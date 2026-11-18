"""LLM service providing intelligent generative capabilities via Groq Cloud.

Powers conversational responses, personalized cover letter enhancements,
and mock interview evaluations with instant fallback to rule-based algorithms.
"""

import logging
from typing import Optional, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class GroqLLMService:
    """Manages Groq Cloud API interactions with automatic error recovery."""

    def __init__(self):
        self._client = None
        self._init_client()

    def _init_client(self):
        if settings.groq_api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=settings.groq_api_key)
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
        """Generate conversational response using Groq LLM."""
        if not self.is_available():
            return None

        system = system_instructions or (
            "You are the IntelliIntern AI Career Companion for the Infosys Springboard VIP 7.0 program. "
            "Help students with internship matching, resume advice, and interview preparation. "
            "Be encouraging, concise, and structured. Only answer queries related to internships, skills, and careers."
        )

        messages = [
            {"role": "system", "content": system},
        ]
        if retrieved_context:
            messages.append({
                "role": "system",
                "content": f"Relevant Internship Data:\n{retrieved_context}"
            })
        messages.append({"role": "user", "content": user_message})

        try:
            resp = self._client.chat.completions.create(
                messages=messages,
                model=settings.groq_model,
                temperature=0.4,
                max_tokens=400,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else None
        except Exception as e:
            logger.warning(f"Groq chat generation failed (falling back): {e}")
            return None

    def generate_cover_letter(
        self,
        candidate_summary: str,
        internship_details: str,
    ) -> Optional[str]:
        """Generate tailored cover letter using Groq LLM."""
        if not self.is_available():
            return None

        prompt = (
            f"Candidate Profile:\n{candidate_summary}\n\n"
            f"Target Internship:\n{internship_details}\n\n"
            "Write a highly professional, 3-paragraph tailored cover letter for this student applying to the internship. "
            "Include an introductory hook, project and skill alignment paragraph, and a proactive closing. "
            "Keep the tone articulate and professional."
        )

        try:
            resp = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert career advisor generating ATS-optimized cover letters."},
                    {"role": "user", "content": prompt},
                ],
                model=settings.groq_model,
                temperature=0.5,
                max_tokens=500,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else None
        except Exception as e:
            logger.warning(f"Groq cover letter generation failed: {e}")
            return None


llm_service = GroqLLMService()
