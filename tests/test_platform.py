"""Tests for Cover Letter Generation, Application Tracking, and Career Chatbot."""

import pytest
from app.routes.platform_routes import (
    apply_to_internship,
    chat_with_assistant,
    generate_cover_letter,
    get_applications,
)
from app.schemas.cover_letter import (
    ApplicationSubmissionRequest,
    ChatbotQueryRequest,
    CoverLetterRequest,
)
from app.schemas.resume import CandidateResume
from app.services.vector_store import vector_store


@pytest.fixture(autouse=True)
def ensure_vector_store():
    """Ensure vector store is loaded prior to tests."""
    if not vector_store.is_loaded():
        vector_store.load_vector_index()


def test_cover_letter_generation_agent():
    """Verify Cover Letter Agent produces tailored letter and ATS scores."""
    req = CoverLetterRequest(
        candidate=CandidateResume(
            name="Aarav Sharma",
            skills=["Java", "Spring Boot", "SQL", "PostgreSQL"],
            projects=["Developed E-Commerce Spring Boot microservice"],
        ),
        internship_id="INT001",
    )
    result = generate_cover_letter(req)

    assert result.candidate_name == "Aarav Sharma"
    assert result.internship_id == "INT001"
    assert "TechNova" in result.company_name
    assert 50 <= result.ats_score <= 100
    assert len(result.tailored_cover_letter) > 100
    assert len(result.ats_suggestions) > 0
    assert "disclaimer" in result.model_dump()


def test_application_tracking_submission():
    """Verify application submission and record tracking."""
    req = ApplicationSubmissionRequest(
        candidate=CandidateResume(
            name="Priya Nair",
            skills=["Python", "FastAPI"],
        ),
        internship_id="INT005",
        cover_letter="My tailored cover letter text.",
    )
    submission = apply_to_internship(req)

    assert submission.application_id.startswith("APP-")
    assert submission.status == "Submitted"
    assert submission.internship_id == "INT005"
    assert submission.candidate_name == "Priya Nair"

    # Verify present in list
    apps = get_applications()
    assert any(a.application_id == submission.application_id for a in apps)


def test_career_chatbot_in_scope_query():
    """Verify chatbot answers in-scope internship questions with RAG retrieval."""
    req = ChatbotQueryRequest(message="What Python backend internships are available?")
    res = chat_with_assistant(req)

    assert res.is_out_of_scope is False
    assert res.guardrail_triggered is False
    assert len(res.retrieved_internships) > 0
    assert "Python" in res.reply


def test_career_chatbot_out_of_scope_guardrail():
    """Verify chatbot triggers guardrails for unrelated topics and politely declines."""
    req = ChatbotQueryRequest(message="What is the weather in Mumbai tomorrow?")
    res = chat_with_assistant(req)

    assert res.is_out_of_scope is True
    assert res.guardrail_triggered is True
    assert "Infosys Springboard Career Assistant" in res.reply
    assert "cannot assist with queries outside this platform" in res.reply
