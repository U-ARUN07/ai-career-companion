"""Internship matching service orchestrating the RAG retrieval pipeline."""

import logging
from typing import Any, Dict, List, Optional, Union
from app.config import settings
from app.schemas.matching import (
    InternshipMatch,
    MatchRequest,
    MatchResponse,
)
from app.schemas.resume import CandidateResume
from app.services.embedding_service import embedding_service
from app.services.explanation_service import explanation_service
from app.services.resume_preprocessor import ResumePreprocessor
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class MatchingService:
    """Orchestrates candidate preprocessing, embedding generation, FAISS retrieval, and ranking."""

    def __init__(self):
        self.preprocessor = ResumePreprocessor()
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.explanation_service = explanation_service

    def find_matches(
        self,
        candidate_data: Union[CandidateResume, Dict[str, Any]],
        top_k: int = settings.default_top_k,
        include_explanation: bool = False,
    ) -> MatchResponse:
        """Execute full matching pipeline for a given candidate resume.

        Pipeline:
        1. Parse & validate candidate resume JSON.
        2. Preprocess resume fields into rich semantic text representation.
        3. Generate L2-normalized candidate embedding.
        4. Execute FAISS inner product similarity search.
        5. Rank and map retrieved metadata into InternshipMatch models.
        6. (Optional) Generate grounded explanations for retrieved roles.
        """
        # Validate candidate schema
        candidate = self.preprocessor.parse_input(candidate_data)

        # Validate top_k
        clamped_k = max(1, min(int(top_k), settings.max_top_k))

        # Check vector store readiness
        if not self.vector_store.is_loaded():
            logger.info("Vector store not in memory. Attempting to load from disk...")
            loaded = self.vector_store.load_vector_index()
            if not loaded:
                raise RuntimeError(
                    "FAISS vector store is not available. Please build the index using 'python scripts/build_vector_database.py'."
                )

        # 1. Preprocess resume to semantic text
        candidate_text = self.preprocessor.preprocess_to_text(candidate)

        # 2. Generate candidate embedding
        candidate_vector = self.embedding_service.encode_text(candidate_text)

        # 3. Retrieve top-k nearest internships
        raw_results = self.vector_store.search_similar_internships(
            query_vector=candidate_vector, top_k=clamped_k
        )

        matches: List[InternshipMatch] = []
        for metadata, score in raw_results:
            match_item = InternshipMatch(
                internship_id=metadata["internship_id"],
                title=metadata["title"],
                company=metadata["company"],
                similarity_score=score,
                description=metadata.get("description", ""),
                required_skills=metadata.get("required_skills", []),
                preferred_skills=metadata.get("preferred_skills"),
                education_requirements=metadata.get("education_requirements"),
                experience_requirements=metadata.get("experience_requirements"),
                location=metadata.get("location", ""),
                work_mode=metadata.get("work_mode", ""),
                duration=metadata.get("duration"),
                stipend=metadata.get("stipend"),
            )

            # 4. Optional grounded explanation
            if include_explanation:
                match_item.explanation = self.explanation_service.generate_explanation(
                    candidate=candidate,
                    internship=metadata,
                    similarity_score=score,
                )

            matches.append(match_item)

        # Sort descending by similarity score
        matches.sort(key=lambda m: m.similarity_score, reverse=True)

        return MatchResponse(
            candidate_name=candidate.name,
            total_matches=len(matches),
            matches=matches,
        )


# Global singleton instance
matching_service = MatchingService()
