"""FAISS-based vector storage and retrieval service.

Provides persistence, indexing, and high-performance semantic search for
normalized internship embeddings using inner product (cosine similarity) search.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import faiss
import numpy as np
from app.config import settings
from app.schemas.internship import Internship

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Manages the FAISS index and associated internship metadata storage."""

    def __init__(
        self,
        index_file: Optional[Path] = None,
        metadata_file: Optional[Path] = None,
        dimension: int = settings.embedding_dimension,
    ):
        self.index_file = index_file or settings.faiss_index_file
        self.metadata_file = metadata_file or settings.metadata_file
        self.dimension = dimension

        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self.id_to_index: Dict[str, int] = {}

    def is_loaded(self) -> bool:
        """Check if index and metadata are currently loaded into memory."""
        return self.index is not None and len(self.metadata) > 0

    def get_total_indexed(self) -> int:
        """Return total number of internships indexed."""
        return self.index.ntotal if self.index is not None else 0

    def build_vector_index(
        self,
        internships: List[Internship],
        embeddings: np.ndarray,
    ) -> faiss.Index:
        """Build FAISS inner product index from normalized embeddings and store metadata.

        Args:
            internships: List of validated Internship schemas.
            embeddings: 2D numpy array of shape (N, dimension) of normalized float32 vectors.
        """
        if len(internships) == 0:
            raise ValueError("Cannot build vector index with an empty internship list.")

        if len(internships) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(internships)} internships provided, but got {len(embeddings)} embeddings."
            )

        # Ensure float32 and 2D
        embeddings_matrix = np.ascontiguousarray(embeddings, dtype=np.float32)
        dim = embeddings_matrix.shape[1]
        self.dimension = dim

        # Use IndexFlatIP (Inner Product). With L2-normalized vectors, IP == Cosine Similarity.
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings_matrix)

        self.index = index
        self.metadata = [item.model_dump() for item in internships]
        self.id_to_index = {item.internship_id: idx for idx, item in enumerate(internships)}

        logger.info(f"Built FAISS index with {index.ntotal} vectors of dimension {dim}")
        return index

    def save_vector_index(
        self,
        index_file: Optional[Path] = None,
        metadata_file: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        """Save FAISS index and metadata to disk."""
        if self.index is None or not self.metadata:
            raise ValueError("No index or metadata in memory to save.")

        idx_path = index_file or self.index_file
        meta_path = metadata_file or self.metadata_file

        idx_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(idx_path))

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved FAISS index to {idx_path} and metadata to {meta_path}")
        return idx_path, meta_path

    def load_vector_index(
        self,
        index_file: Optional[Path] = None,
        metadata_file: Optional[Path] = None,
    ) -> bool:
        """Load saved FAISS index and metadata from disk."""
        idx_path = index_file or self.index_file
        meta_path = metadata_file or self.metadata_file

        if not idx_path.exists() or not meta_path.exists():
            logger.warning(f"Index or metadata file missing: {idx_path}, {meta_path}")
            return False

        try:
            self.index = faiss.read_index(str(idx_path))
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            self.id_to_index = {
                item["internship_id"]: idx for idx, item in enumerate(self.metadata)
            }
            logger.info(
                f"Successfully loaded FAISS index with {self.index.ntotal} records from {idx_path}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}", exc_info=True)
            self.index = None
            self.metadata = []
            self.id_to_index = {}
            return False

    def search_similar_internships(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search top-k most semantically similar internships for a candidate vector.

        Returns:
            List of tuples: (internship_metadata_dict, similarity_score)
            sorted descending by similarity score.
        """
        if not self.is_loaded():
            raise RuntimeError("Vector database is not loaded. Build or load the index first.")

        # Ensure 2D float32
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)
        query_vector = np.ascontiguousarray(query_vector, dtype=np.float32)

        # Clamp top_k to available vectors
        total = self.index.ntotal
        effective_k = min(max(1, top_k), total)

        distances, indices = self.index.search(query_vector, effective_k)

        results: List[Tuple[Dict[str, Any], float]] = []
        seen_ids = set()

        for idx, score in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            item = self.metadata[idx]
            internship_id = item["internship_id"]
            if internship_id not in seen_ids:
                seen_ids.add(internship_id)
                # Cosine similarity score bounded to [-1.0, 1.0], rounded to 4 decimals
                norm_score = float(np.clip(score, -1.0, 1.0))
                results.append((item, round(norm_score, 4)))

        return results


# Global singleton instance for application reuse
vector_store = VectorStoreService()
