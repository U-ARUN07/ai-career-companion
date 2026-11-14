"""Unit tests for candidate resume preprocessing."""

import pytest
from app.schemas.resume import CandidateResume
from app.services.resume_preprocessor import ResumePreprocessor


def test_resume_preprocessing_complete_profile():
    """Test preprocessing with a fully populated candidate profile."""
    data = {
        "name": "Candidate A",
        "summary": "Computer Science student interested in backend development",
        "skills": ["Java", "Spring Boot", "SQL", "REST APIs"],
        "education": ["B.Tech Computer Science"],
        "projects": ["Developed a REST API using Spring Boot and MySQL"],
        "experience": ["Intern at Tech Corp"],
        "certifications": ["Java Full Stack"],
        "achievements": ["Hackathon Winner 2024"],
    }
    processed_text = ResumePreprocessor.preprocess_to_text(data)

    assert "Candidate Profile: Candidate A" in processed_text
    assert "Professional Summary: Computer Science student interested in backend development" in processed_text
    assert "Technical and Core Skills: Java, Spring Boot, SQL, REST APIs" in processed_text
    assert "Key Projects: Developed a REST API using Spring Boot and MySQL" in processed_text
    assert "Education: B.Tech Computer Science" in processed_text
    assert "Certifications: Java Full Stack" in processed_text


def test_resume_preprocessing_missing_and_null_fields():
    """Test preprocessing when optional fields are null or empty lists."""
    data = {
        "name": "Candidate B",
        "summary": None,
        "skills": ["Python", "FastAPI"],
        "education": None,
        "projects": ["Built API"],
        "experience": [],
        "certifications": None,
        "achievements": [],
    }
    processed_text = ResumePreprocessor.preprocess_to_text(data)

    assert "Candidate Profile: Candidate B" in processed_text
    assert "Technical and Core Skills: Python, FastAPI" in processed_text
    assert "Key Projects: Built API" in processed_text
    # Should not produce null strings or blank sections
    assert "None" not in processed_text


def test_resume_preprocessing_empty_input():
    """Test preprocessing when an empty candidate object is supplied."""
    empty_data = {}
    processed_text = ResumePreprocessor.preprocess_to_text(empty_data)

    assert isinstance(processed_text, str)
    assert len(processed_text) > 0
    assert "Entry-level candidate" in processed_text


def test_resume_preserves_technical_skills():
    """Ensure technical skills with symbols (C++, C#, .NET) are safely maintained."""
    data = {
        "name": "Systems Dev",
        "skills": ["C++", "C#", ".NET", "Node.js"],
        "projects": ["Engineered low-latency C++ trading simulator"],
    }
    resume = ResumePreprocessor.parse_input(data)
    assert "C++" in resume.skills
    assert "C#" in resume.skills
    assert ".NET" in resume.skills

    text = ResumePreprocessor.preprocess_to_text(resume)
    assert "C++" in text
    assert "C#" in text
