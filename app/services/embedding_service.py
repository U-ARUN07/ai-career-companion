"""Embedding service using Sentence Transformers with robust fallback support.

Generates normalized 384-dimensional vector embeddings for candidate resume text and
internship opportunities, supporting batch encoding, normalization, and safe empty-input handling.
"""

import logging
from typing import List, Optional
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service to load SentenceTransformer models and encode text into normalized vectors.

    Features:
    - Primary Engine: sentence-transformers/all-MiniLM-L6-v2 (384-dim dense vectors)
    - Fallback Engine: Deterministic 384-dim normalized lexical feature projection
      (ensures the system functions even in constrained offline environments without crashing)
    - Normalization: L2 unit normalization ensuring Inner Product == Cosine Similarity
    - Safe Handling: Empty/null text returns a valid normalized neutral unit vector.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        dimension: int = settings.embedding_dimension,
        normalize: bool = settings.normalize_embeddings,
    ):
        self.model_name = model_name or settings.embedding_model
        self.dimension = dimension
        self.normalize = normalize
        self._model = None
        self._is_fallback = False

    def _get_model(self):
        """Lazy loader for SentenceTransformer model with graceful fallback."""
        if self._model is None:
            try:
                logger.info(f"Loading primary embedding model: {self.model_name}...")
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(self.model_name)
                test_dim = model.get_sentence_embedding_dimension()
                if test_dim:
                    self.dimension = test_dim
                self._model = model
                self._is_fallback = False
                logger.info(f"SentenceTransformer {self.model_name} loaded successfully (dim={self.dimension}).")
            except Exception as e:
                logger.warning(
                    f"SentenceTransformer unavailable or still initializing ({e}). "
                    f"Activating deterministic {self.dimension}-dim semantic fallback engine."
                )
                self._is_fallback = True
                self._model = "fallback"

        return self._model

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Deterministic 384-dim normalized projection based on token hashing.

        Maintains exact 384-dim contract and produces positive inner products for overlapping
        skills and project keywords.
        """
        from sklearn.feature_extraction.text import HashingVectorizer

        vectorizer = HashingVectorizer(
            n_features=self.dimension,
            norm="l2",
            alternate_sign=False,
            token_pattern=r"(?u)\b\w+\b",
        )
        sparse_vecs = vectorizer.transform(texts)
        dense_vecs = sparse_vecs.toarray().astype(np.float32)

        # Ensure no zero vectors (neutral unit vector fallback)
        norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
        zero_mask = (norms == 0).flatten()
        if np.any(zero_mask):
            dense_vecs[zero_mask, 0] = 1.0

        if self.normalize:
            norms = np.linalg.norm(dense_vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            dense_vecs = dense_vecs / norms

        return dense_vecs

    def encode_text(self, text: str) -> np.ndarray:
        """Encode a single text string into a normalized 1D float32 vector of shape (dimension,)."""
        if not text or not text.strip():
            # Return normalized unit vector for empty input to prevent NaN
            vec = np.zeros(self.dimension, dtype=np.float32)
            vec[0] = 1.0
            return vec

        model = self._get_model()

        if self._is_fallback:
            return self._fallback_encode([text])[0]

        vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=self.normalize)
        vec = np.array(vec, dtype=np.float32)

        if self.normalize:
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm

        return vec

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode a list of texts into a 2D float32 array of shape (N, dimension)."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        sanitized_texts = [
            t.strip() if (t and isinstance(t, str) and t.strip()) else "Candidate Profile"
            for t in texts
        ]

        model = self._get_model()

        if self._is_fallback:
            return self._fallback_encode(sanitized_texts)

        vectors = model.encode(
            sanitized_texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize,
        )
        vectors = np.array(vectors, dtype=np.float32)

        if self.normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vectors = vectors / norms

        return vectors


# Global singleton instance for application reuse
embedding_service = EmbeddingService()
