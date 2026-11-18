"""Tests for Interview Preparation and Question Generation Agent."""

from app.routes.interview_routes import (
    generate_interview_questions,
    evaluate_practice_answer,
    InterviewQuestionsRequest,
    InterviewEvaluationRequest,
)


def test_interview_questions_generation():
    req = InterviewQuestionsRequest(
        internship_id="INT001",
        candidate_skills=["Python", "Machine Learning", "FastAPI", "PyTorch"],
    )
    data = generate_interview_questions(req)
    assert data["internship_id"] == "INT001"
    assert len(data["questions"]) == 5
    first_q = data["questions"][0]
    assert "question" in first_q
    assert "topics_tested" in first_q
    assert "interviewer_focus" in first_q


def test_interview_answer_evaluation():
    req = InterviewEvaluationRequest(
        question="How have you applied Python in your recent projects?",
        answer=(
            "In my recent project, the Situation was building a high-throughput RAG search platform. "
            "My Task was reducing vector query latency. I took Action by using FAISS IndexFlatIP with "
            "normalized embeddings and batched tensor inference. The Result was a sub-50ms query response time."
        ),
        category="Technical",
    )
    data = evaluate_practice_answer(req)
    assert data["score"] >= 75
    assert data["star_framework_applied"] is True
    assert "feedback" in data
