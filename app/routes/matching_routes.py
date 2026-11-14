"""Internship matching endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.config import settings
from app.schemas.internship import Internship
from app.schemas.matching import MatchRequest, MatchResponse
from app.services.internship_loader import InternshipLoader
from app.services.matching_service import matching_service

router = APIRouter(prefix="/api/v1/matching", tags=["Internship Matching"])
loader = InternshipLoader()


@router.post(
    "/internships",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic Candidate-to-Internship Matching",
)
def match_candidate_internships(request: MatchRequest):
    """Perform RAG semantic similarity matching for a candidate resume.

    Accepts structured candidate resume JSON, produces normalized vector embedding,
    queries the FAISS vector database using cosine similarity, and returns the top_k
    ranked internship recommendations with similarity scores and optional grounded explanations.
    """
    try:
        results = matching_service.find_matches(
            candidate_data=request.candidate,
            top_k=request.top_k,
            include_explanation=request.include_explanation,
        )
        return results
    except RuntimeError as re:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(re),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during internship matching: {str(e)}",
        )


@router.get(
    "/internships/{internship_id}",
    response_model=Internship,
    status_code=status.HTTP_200_OK,
    summary="Get Internship Details by ID",
)
def get_internship_by_id(internship_id: str):
    """Retrieve full details of a specific synthetic internship by its ID (e.g., INT001)."""
    internship = loader.get_by_id(internship_id)
    if not internship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Internship with ID '{internship_id}' not found in the dataset.",
        )
    return internship


@router.get(
    "/internships",
    response_model=List[Internship],
    status_code=status.HTTP_200_OK,
    summary="List All Internships",
)
def list_internships(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Offset items"),
):
    """List loaded synthetic internships with pagination support."""
    internships = loader.load_dataset()
    return internships[offset : offset + limit]
