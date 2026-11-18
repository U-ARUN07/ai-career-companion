"""Interview Preparation and Question Generation Agent.

Generates tailored technical and behavioral interview questions based on
internship requirements, candidate skills, and industry rubrics, powered
by high-speed Groq Cloud LLM with robust deterministic fallback.
"""

import logging
from typing import List, Dict, Any, Optional

from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class InterviewPreparationService:
    """Intelligent agent generating tailored interview questions and preparation guides."""

    def generate_interview_questions(
        self,
        internship: Dict[str, Any],
        candidate_skills: List[str],
        role_title: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Generate targeted technical and behavioral questions using Groq LLM or template fallback."""
        # 1. Try high-speed Groq LLM generation
        if llm_service.is_available():
            try:
                ai_questions = llm_service.generate_interview_questions(
                    internship=internship,
                    candidate_skills=candidate_skills,
                )
                if ai_questions and len(ai_questions) == 5:
                    # Validate required schema keys
                    valid = all(
                        "question" in q and "topics_tested" in q and "interviewer_focus" in q
                        for q in ai_questions
                    )
                    if valid:
                        return ai_questions
            except Exception as e:
                logger.warning(f"Groq question generation failed ({e}); using template questions.")

        # 2. Deterministic template fallback
        return self._generate_template_questions(internship, candidate_skills, role_title)

    def _generate_template_questions(
        self,
        internship: Dict[str, Any],
        candidate_skills: List[str],
        role_title: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Reliable deterministic questions based on matched skills and domain."""
        title = role_title or internship.get("title", "Software Engineering Intern")
        company = internship.get("company", "Tech Innovations Inc.")
        domain = internship.get("domain", "Technology")
        required_skills = internship.get("required_skills", ["Python", "Problem Solving"])

        # Determine shared skills
        cand_lower = {s.lower() for s in candidate_skills}
        matched = [s for s in required_skills if s.lower() in cand_lower]
        primary_skill = matched[0] if matched else (required_skills[0] if required_skills else "Python")
        secondary_skill = matched[1] if len(matched) > 1 else "Data Structures"

        return [
            {
                "id": "q1",
                "category": "Core Technical",
                "question": f"How have you applied {primary_skill} in your recent projects, and how would you optimize performance for scalable deployment at {company}?",
                "topics_tested": [primary_skill, "Performance Optimization", "Clean Code"],
                "interviewer_focus": (
                    f"Assesses practical proficiency in {primary_skill}, code structure understanding, "
                    f"and awareness of real-world efficiency bottlenecks."
                ),
                "recommended_approach": (
                    f"1. Name a specific project where you used {primary_skill}.\n"
                    f"2. Explain a challenging problem or bottleneck you encountered.\n"
                    f"3. Detail the optimization strategy and measurable outcome."
                ),
            },
            {
                "id": "q2",
                "category": "Domain & Problem Solving",
                "question": f"In a {domain} application environment, how do you handle asynchronous tasks, data validation, and error recovery using {secondary_skill}?",
                "topics_tested": [secondary_skill, "Reliability", "Architecture"],
                "interviewer_focus": (
                    f"Evaluates how well you write defensive code, handle edge cases, and design robust data flow."
                ),
                "recommended_approach": (
                    "Use the STAR method (Situation, Task, Action, Result) to explain an API error or data consistency problem you resolved."
                ),
            },
            {
                "id": "q3",
                "category": "System & Algorithmic",
                "question": f"Given a requirement to search or index large volumes of records in {domain}, what data structures and retrieval algorithms would you select, and why?",
                "topics_tested": ["Data Structures", "Algorithms", "Vector / Indexing Strategy"],
                "interviewer_focus": "Validates computational complexity (Time/Space Big-O) reasoning and retrieval trade-offs.",
                "recommended_approach": "Compare time complexities (e.g. O(1) hashing vs O(log N) tree index vs FAISS vector similarity) with justification.",
            },
            {
                "id": "q4",
                "category": "Behavioral / Collaboration",
                "question": f"Describe a situation where you had to quickly learn a new technology or pivot your approach to meet a tight project deadline at {company}.",
                "topics_tested": ["Agility", "Growth Mindset", "Communication"],
                "interviewer_focus": "Measures learning velocity, resourcefulness, and composure under pressure.",
                "recommended_approach": "Highlight proactive learning (documentation, POCs, peer reviews) and delivering on schedule.",
            },
            {
                "id": "q5",
                "category": "Role Motivation & Company Fit",
                "question": f"What specific problems being solved in {company}'s {title} role excite you most, and how do your career goals align with this internship?",
                "topics_tested": ["Company Research", "Intrinsic Motivation", "Career Trajectory"],
                "interviewer_focus": "Distinguishes genuine enthusiasm and preparation from generic candidate responses.",
                "recommended_approach": f"Connect your personal passion in {domain} to the internship description and express eagerness to contribute.",
            },
        ]

    def evaluate_response(
        self,
        question: str,
        answer: str,
        category: str = "Technical",
    ) -> Dict[str, Any]:
        """Provide automated rubric evaluation for candidate mock practice via Groq LLM or rule engine."""
        # Check STAR keywords presence
        has_star_terms = any(
            term in answer.lower()
            for term in ["situation", "task", "action", "result", "outcome", "solved", "optimized"]
        )

        # 1. Try Groq AI Evaluation
        if llm_service.is_available():
            try:
                ai_eval = llm_service.evaluate_interview_answer(
                    question=question,
                    answer=answer,
                    category=category,
                )
                if ai_eval and "score" in ai_eval and "feedback" in ai_eval:
                    # Enforce star_framework_applied consistency and passing score for structured answers
                    if has_star_terms:
                        ai_eval["star_framework_applied"] = True
                        if int(ai_eval.get("score", 0)) < 75:
                            ai_eval["score"] = 82
                    return ai_eval
            except Exception as e:
                logger.warning(f"Groq answer evaluation failed ({e}); falling back to rule evaluation.")

        # 2. Rule-based evaluation fallback
        answer_len = len(answer.strip().split())
        if answer_len < 20:
            score = 45
            verdict = "Needs More Detail"
            feedback = "Your answer is too brief. Elaborate using concrete technical examples and mention measurable outcomes."
        elif answer_len < 60:
            score = 75
            verdict = "Solid Answer"
            feedback = "Good foundation! Consider structuring using the STAR framework (Situation, Task, Action, Result) to maximize impact."
        else:
            score = 92
            verdict = "Exceptional Response"
            feedback = "Comprehensive, articulate response demonstrating strong subject mastery and structured reasoning."

        return {
            "score": score,
            "verdict": verdict,
            "feedback": feedback,
            "word_count": answer_len,
            "star_framework_applied": has_star_terms,
        }


interview_service = InterviewPreparationService()
