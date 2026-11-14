"""Health check and system status routes."""

from fastapi import APIRouter
from app.config import settings
from app.services.vector_store import vector_store

router = APIRouter(tags=["Health"])


@router.get("/health", summary="System Health and Vector Database Status")
def health_check():
    """Return application health, embedding model info, and vector database status."""
    is_index_loaded = vector_store.is_loaded()
    total_indexed = vector_store.get_total_indexed()

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "vector_database": {
            "is_loaded": is_index_loaded,
            "total_indexed_internships": total_indexed,
            "embedding_dimension": settings.embedding_dimension,
            "index_path": str(settings.faiss_index_file),
        },
        "embedding_model": settings.embedding_model,
        "explanation_provider": settings.explanation_provider,
    }
