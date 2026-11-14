"""Unit tests for embedding generation."""

import numpy as np
import pytest
from app.services.embedding_service import embedding_service


def test_embedding_single_text():
    """Verify single text generates a normalized 1D vector of expected dimension."""
    text = "Java Spring Boot REST API developer with PostgreSQL knowledge."
    vec = embedding_service.encode_text(text)

    assert isinstance(vec, np.ndarray)
    assert vec.ndim == 1
    assert vec.shape[0] == embedding_service.dimension
    # Test L2 normalization: norm should be approximately 1.0
    norm = np.linalg.norm(vec)
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_embedding_batch_generation():
    """Verify batch text encoding returns a 2D float32 matrix."""
    texts = [
        "Python data scientist with Pandas and Machine Learning experience",
        "React frontend developer proficient in Tailwind CSS and TypeScript",
        "DevOps engineer managing AWS EC2 and Kubernetes clusters",
    ]
    matrix = embedding_service.encode_batch(texts)

    assert isinstance(matrix, np.ndarray)
    assert matrix.ndim == 2
    assert matrix.shape[0] == len(texts)
    assert matrix.shape[1] == embedding_service.dimension

    # Each row should be unit normalized
    row_norms = np.linalg.norm(matrix, axis=1)
    for r_norm in row_norms:
        assert pytest.approx(r_norm, rel=1e-3) == 1.0


def test_embedding_empty_text_safety():
    """Ensure empty or blank strings return a valid normalized vector without exceptions."""
    empty_vec = embedding_service.encode_text("")
    assert isinstance(empty_vec, np.ndarray)
    assert empty_vec.shape[0] == embedding_service.dimension
    assert not np.isnan(empty_vec).any()

    whitespace_vec = embedding_service.encode_text("   \n\t  ")
    assert isinstance(whitespace_vec, np.ndarray)
    assert whitespace_vec.shape[0] == embedding_service.dimension
    assert not np.isnan(whitespace_vec).any()


def test_embedding_dimension_consistency():
    """Ensure consistent dimensions across multiple different inputs."""
    dim = embedding_service.dimension
    assert embedding_service.encode_text("Short").shape[0] == dim
    assert embedding_service.encode_text("Very long detailed project description with many technical details" * 10).shape[0] == dim
