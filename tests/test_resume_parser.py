"""Tests for Resume Parsing and Skill Extraction Service."""

from app.services.resume_parser import resume_parser
from app.services.matching_service import matching_service


def test_resume_parser_heuristics():
    text = """
    Arun
    Summary: Computer science student enthusiastic about Python, Machine Learning, and APIs.
    Education:
    B.Tech Computer Science and Engineering, CGPA 8.9, 2022-2026
    Skills: Python, FastAPI, Docker, PyTorch, React, Git, SQL
    Projects:
    Built an end-to-end RAG internship matching system using Sentence Transformers and FAISS.
    """
    resume = resume_parser.parse_to_candidate_resume(text, default_name="Arun")
    assert resume.name == "Arun"
    assert "Python" in resume.skills
    assert "FastAPI" in resume.skills
    assert "Docker" in resume.skills
    assert len(resume.education) > 0


def test_parsed_resume_matching_pipeline():
    text = """
    Arun
    Skills: Python, FastAPI, Machine Learning, PyTorch, SQL, Git, Docker
    Education: B.Tech in Computer Science
    Projects: Deep Learning Image Classifier with PyTorch and FastAPI
    """
    candidate_resume = resume_parser.parse_to_candidate_resume(text, default_name="Arun")
    matches = matching_service.find_matches(candidate_data=candidate_resume, top_k=3)

    assert matches.candidate_name == "Arun"
    assert matches.total_matches == 3
    assert len(matches.matches) == 3
    assert matches.matches[0].similarity_score > 0
