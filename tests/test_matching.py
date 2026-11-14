"""Unit tests for FAISS vector store, retrieval, and matching service."""

import json
from pathlib import Path
import pytest
from app.config import settings
from app.schemas.internship import Internship
from app.services.embedding_service import embedding_service
from app.services.internship_loader import InternshipLoader
from app.services.matching_service import matching_service
from app.services.vector_store import VectorStoreService, vector_store


def test_vector_store_build_and_search(tmp_path: Path):
    """Test FAISS index creation, persistence, and inner product retrieval."""
    test_store = VectorStoreService(
        index_file=tmp_path / "test_faiss.bin",
        metadata_file=tmp_path / "test_meta.json",
        dimension=embedding_service.dimension,
    )

    internships = [
        Internship(
            internship_id="T01",
            title="Java Backend Intern",
            company="Tech Corp",
            description="Work with Spring Boot and SQL",
            required_skills=["Java", "Spring Boot", "SQL"],
            location="Bangalore",
            work_mode="Remote",
            duration="3 months",
            stipend="₹15,000",
        ),
        Internship(
            internship_id="T02",
            title="Python ML Intern",
            company="AI Labs",
            description="Build machine learning models with PyTorch",
            required_skills=["Python", "Machine Learning", "PyTorch"],
            location="Hyderabad",
            work_mode="Hybrid",
            duration="6 months",
            stipend="₹20,000",
        ),
    ]

    texts = [InternshipLoader.format_internship_to_text(i) for i in internships]
    embeddings = embedding_service.encode_batch(texts)

    test_store.build_vector_index(internships, embeddings)
    assert test_store.is_loaded()
    assert test_store.get_total_indexed() == 2

    # Save and reload
    test_store.save_vector_index()
    assert (tmp_path / "test_faiss.bin").exists()
    assert (tmp_path / "test_meta.json").exists()

    new_store = VectorStoreService(
        index_file=tmp_path / "test_faiss.bin",
        metadata_file=tmp_path / "test_meta.json",
    )
    loaded = new_store.load_vector_index()
    assert loaded is True
    assert new_store.get_total_indexed() == 2

    # Search with a Java query
    query_vec = embedding_service.encode_text("Java Spring Boot Developer with SQL skills")
    results = new_store.search_similar_internships(query_vec, top_k=2)

    assert len(results) == 2
    top_match, top_score = results[0]
    assert top_match["internship_id"] == "T01"
    assert top_score >= results[1][1]


def test_top_k_retrieval_and_ordering():
    """Verify top_k constraints and strictly descending similarity score ordering."""
    candidate = {
        "name": "Backend Candidate",
        "skills": ["Java", "Spring Boot", "PostgreSQL"],
        "projects": ["Built REST microservices using Spring Boot"],
    }
    resp = matching_service.find_matches(candidate, top_k=5)
    assert resp.total_matches == 5
    assert len(resp.matches) == 5

    # Check scores are sorted descending
    scores = [m.similarity_score for m in resp.matches]
    assert scores == sorted(scores, reverse=True)


def test_duplicate_internship_id_rejection(tmp_path: Path):
    """Ensure loader rejects duplicate internship IDs with a descriptive error."""
    dup_file = tmp_path / "dup_internships.json"
    dup_data = [
        {
            "internship_id": "DUP01",
            "title": "Role A",
            "company": "Company A",
            "description": "Desc A",
            "required_skills": ["Python"],
            "location": "City",
            "work_mode": "Remote",
            "duration": "3m",
            "stipend": "10k",
        },
        {
            "internship_id": "DUP01",
            "title": "Role B",
            "company": "Company B",
            "description": "Desc B",
            "required_skills": ["Java"],
            "location": "City",
            "work_mode": "Hybrid",
            "duration": "3m",
            "stipend": "10k",
        },
    ]
    with open(dup_file, "w", encoding="utf-8") as f:
        json.dump(dup_data, f)

    loader = InternshipLoader(dup_file)
    with pytest.raises(ValueError, match="Duplicate internship ID detected"):
        loader.load_dataset()


def test_empty_internship_dataset_rejection(tmp_path: Path):
    """Ensure vector store rejects index creation with empty dataset."""
    empty_store = VectorStoreService()
    import numpy as np
    with pytest.raises(ValueError, match="Cannot build vector index with an empty"):
        empty_store.build_vector_index([], np.empty((0, 384), dtype=np.float32))


def test_matching_with_grounded_explanation():
    """Test matching request with explanation generation enabled."""
    candidate = {
        "name": "Full Stack Dev",
        "skills": ["React", "Node.js", "Express.js", "MongoDB"],
        "projects": ["MERN stack e-commerce web app"],
    }
    resp = matching_service.find_matches(candidate, top_k=3, include_explanation=True)
    assert resp.total_matches == 3
    for match in resp.matches:
        assert match.explanation is not None
        assert len(match.explanation.match_reason) > 0
        assert len(match.explanation.recommendation) > 0
        assert "disclaimer" in match.explanation.model_dump()
