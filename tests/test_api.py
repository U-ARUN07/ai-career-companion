"""API endpoint and route handler integration tests.

Tests FastAPI route handlers, Pydantic request/response validation,
HTTP exception behavior, and route registrations.
"""

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.main import app
from app.routes.health_routes import health_check
from app.routes.matching_routes import (
    get_internship_by_id,
    list_internships,
    match_candidate_internships,
)
from app.schemas.matching import MatchRequest
from app.services.vector_store import vector_store


@pytest.fixture(autouse=True)
def ensure_vector_store():
    """Ensure vector store is loaded prior to API tests."""
    if not vector_store.is_loaded():
        vector_store.load_vector_index()


def test_routes_registered_on_app():
    """Verify all required endpoints are properly registered on the FastAPI app."""
    registered_paths = [route.path for route in app.routes]

    assert "/health" in registered_paths
    assert "/api/v1/matching/internships" in registered_paths
    assert "/api/v1/matching/internships/{internship_id}" in registered_paths


def test_health_endpoint():
    """Verify health endpoint returns status, embedding model, and vector DB info."""
    data = health_check()
    assert data["status"] == "healthy"
    assert "vector_database" in data
    assert data["vector_database"]["is_loaded"] is True
    assert data["vector_database"]["total_indexed_internships"] >= 50
    assert "embedding_model" in data


def test_matching_endpoint_success():
    """Verify matching endpoint handles candidate resume and returns ranked matches."""
    request = MatchRequest(
        candidate={
            "name": "Candidate A",
            "summary": "Computer Science student interested in backend development",
            "skills": ["Java", "Spring Boot", "SQL"],
            "education": ["B.Tech Computer Science"],
            "projects": ["Developed REST APIs using Spring Boot"],
            "experience": [],
            "certifications": ["Java Full Stack"],
        },
        top_k=5,
    )

    response = match_candidate_internships(request)

    assert response.candidate_name == "Candidate A"
    assert response.total_matches == 5
    assert len(response.matches) == 5

    first_match = response.matches[0]
    assert first_match.internship_id.startswith("INT")
    assert first_match.title
    assert first_match.company
    assert 0.0 <= first_match.similarity_score <= 1.0
    assert first_match.required_skills


def test_matching_endpoint_with_explanation():
    """Verify matching endpoint produces grounded RAG explanations when requested."""
    request = MatchRequest(
        candidate={
            "name": "Candidate RAG",
            "skills": ["Python", "FastAPI", "SQL"],
            "projects": ["Built FastAPI microservice"],
        },
        top_k=3,
        include_explanation=True,
    )

    response = match_candidate_internships(request)
    assert len(response.matches) == 3

    for match in response.matches:
        assert match.explanation is not None
        assert match.explanation.match_reason
        assert isinstance(match.explanation.matching_skills, list)
        assert isinstance(match.explanation.missing_required_skills, list)
        assert match.explanation.recommendation
        assert match.explanation.disclaimer


def test_matching_endpoint_top_k_validation():
    """Verify top_k bounds validation (clamped or rejected by schema)."""
    # top_k > 50 must raise ValidationError
    with pytest.raises(ValidationError):
        MatchRequest(
            candidate={"name": "Test"},
            top_k=100,
        )

    # top_k < 1 must raise ValidationError
    with pytest.raises(ValidationError):
        MatchRequest(
            candidate={"name": "Test"},
            top_k=0,
        )


def test_get_internship_by_id_success():
    """Verify retrieving existing internship by its ID (e.g. INT001)."""
    internship = get_internship_by_id("INT001")
    assert internship.internship_id == "INT001"
    assert "Java" in internship.title or "Java" in internship.required_skills


def test_get_internship_by_id_not_found():
    """Verify retrieving non-existent internship ID raises 404 HTTPException."""
    with pytest.raises(HTTPException) as exc_info:
        get_internship_by_id("NON_EXISTENT_ID_999")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_list_internships_endpoint():
    """Verify pagination when listing internships."""
    items = list_internships(limit=10, offset=0)
    assert isinstance(items, list)
    assert len(items) == 10

    next_page = list_internships(limit=10, offset=10)
    assert len(next_page) == 10
    # Ensure distinct items
    assert items[0].internship_id != next_page[0].internship_id
