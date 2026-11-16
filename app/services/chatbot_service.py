"""Conversational Career Assistant with Safety Guardrails.

RAG-powered conversational assistant to help users navigate the internship matching platform,
equipped with strict safety guardrails to politely decline out-of-scope queries and
prevent hallucinations when retrieval produces no results.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from app.config import settings
from app.schemas.cover_letter import ChatbotQueryResponse
from app.schemas.resume import CandidateResume
from app.services.embedding_service import embedding_service
from app.services.internship_loader import InternshipLoader
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

# Out-of-scope intent keywords / topics
OUT_OF_SCOPE_PATTERNS = [
    r"\b(weather|recipe|cooking|movie|celebrity|football|cricket|sports score|politics|election|president|prime minister)\b",
    r"\b(joke|riddle|song lyrics|poem|horoscope|astrology|crypto price|bitcoin)\b",
    r"\b(how to hack|make a bomb|bypass security|crack password)\b",
]

IN_SCOPE_KEYWORDS = [
    "internship", "intern", "job", "role", "apply", "application", "resume",
    "skills", "java", "python", "data", "ml", "ai", "cloud", "aws", "devops",
    "cyber", "react", "spring", "stipend", "duration", "location", "remote",
    "hybrid", "cover letter", "ats", "matching", "infosys", "career",
]


class CareerChatbotService:
    """Conversational assistant with RAG grounding and guardrails."""

    def __init__(self):
        self.loader = InternshipLoader()
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def is_out_of_scope(self, query: str) -> bool:
        """Check if user query violates the platform scope boundary."""
        clean_q = query.strip().lower()

        # Check explicit negative patterns
        for pattern in OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, clean_q):
                return True

        # If very generic query that has none of the career/internship keywords
        words = set(re.findall(r"\w+", clean_q))
        has_career_keyword = any(k in clean_q for k in IN_SCOPE_KEYWORDS)

        # Allow basic greetings
        if clean_q in ["hi", "hello", "hey", "help", "who are you", "what can you do"]:
            return False

        # If length > 20 chars and zero career keywords, flag as out of scope
        if len(clean_q) > 25 and not has_career_keyword:
            return True

        return False

    def answer_query(
        self, query: str, candidate_context: Optional[CandidateResume] = None
    ) -> ChatbotQueryResponse:
        """Process query, apply guardrails, retrieve ground-truth context, and generate answer."""
        clean_q = query.strip()

        # 1. Guardrail Check: Out-of-scope query
        if self.is_out_of_scope(clean_q):
            return ChatbotQueryResponse(
                reply=(
                    "I am your Infosys Springboard Career Assistant, dedicated exclusively to "
                    "internship discovery, resume matching, and application guidance. "
                    "I cannot assist with queries outside this platform. "
                    "Please ask me about available internships (e.g., Python, Java, AI/ML), "
                    "application requirements, or cover letter generation."
                ),
                is_out_of_scope=True,
                guardrail_triggered=True,
                retrieved_internships=[],
            )

        # 2. Handle Basic Greetings
        if clean_q.lower() in ["hi", "hello", "hey", "help", "who are you", "what can you do"]:
            total_roles = self.vector_store.get_total_indexed() or 55
            return ChatbotQueryResponse(
                reply=(
                    f"Hello! I am your RAG Career Assistant for the Infosys Springboard VIP 7.0 platform. "
                    f"I can help you navigate our catalog of {total_roles} synthetic internship opportunities, "
                    f"explain how semantic matching works, or guide your application submissions. "
                    f"Try asking: 'Show me remote Python internships' or 'What are the top roles for Java?'"
                ),
                is_out_of_scope=False,
                guardrail_triggered=False,
                retrieved_internships=[],
            )

        # 3. RAG Retrieval via Vector Store
        if not self.vector_store.is_loaded():
            self.vector_store.load_vector_index()

        query_vec = self.embedding_service.encode_text(clean_q)
        results = self.vector_store.search_similar_internships(query_vec, top_k=3)

        # 4. Anti-Hallucination Guardrail: Retrieval failure threshold
        if not results or (results and results[0][1] < 0.15):
            return ChatbotQueryResponse(
                reply=(
                    "No verified internship opportunities in our catalog closely matched your query. "
                    "To prevent generating inaccurate information, I only reference available opportunities. "
                    "Please consider refining your search to active domains like Java Backend, Python, "
                    "Full Stack, Data Science, AI/ML, Cloud Computing, or Cybersecurity."
                ),
                is_out_of_scope=False,
                guardrail_triggered=True,
                retrieved_internships=[],
            )

        # 5. Format Grounded Response
        top_items = [item for item, score in results]
        lines = [
            f"Here are the most relevant internship opportunities found in our catalog for '{clean_q}':\n"
        ]

        for idx, (item, score) in enumerate(results, start=1):
            lines.append(
                f"{idx}. **{item['title']}** at **{item['company']}**\n"
                f"   - **ID:** `{item['internship_id']}` | **Location:** {item['location']} ({item['work_mode']})\n"
                f"   - **Required Skills:** {', '.join(item.get('required_skills', [])[:4])}\n"
                f"   - **Stipend:** {item.get('stipend', 'N/A')} | **Duration:** {item.get('duration', 'N/A')}\n"
                f"   - **Semantic Similarity Score:** `{score:.4f}`"
            )

        lines.append(
            "\nYou can apply directly to any of these roles using the Application Tracking module or generate a tailored cover letter!"
        )

        return ChatbotQueryResponse(
            reply="\n".join(lines),
            is_out_of_scope=False,
            guardrail_triggered=False,
            retrieved_internships=top_items,
        )


chatbot_service = CareerChatbotService()
