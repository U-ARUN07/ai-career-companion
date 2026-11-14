"""Main FastAPI application entry point for RAG-based Internship Matching System."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config import settings
from app.routes.health_routes import router as health_router
from app.routes.matching_routes import router as matching_router
from app.services.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag_internship_matching")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Automatically ensures the vector database is built and loaded into memory on startup
    so the live cloud deployment or local server responds immediately without manual preparation.
    """
    logger.info("Initializing RAG Internship Matching System...")

    # Auto-build vector store if missing on disk (e.g. fresh cloud deployment)
    if not (settings.faiss_index_file.exists() and settings.metadata_file.exists()):
        logger.info("FAISS vector index not found on disk. Auto-building index on startup...")
        try:
            from scripts.build_vector_database import build_and_save_vector_database

            build_and_save_vector_database()
        except Exception as e:
            logger.error(f"Failed to auto-build vector database on startup: {e}", exc_info=True)

    # Load into memory
    loaded = vector_store.load_vector_index()
    if loaded:
        logger.info(
            f"Vector database ready: {vector_store.get_total_indexed()} internships loaded."
        )
    else:
        logger.warning("Vector database could not be loaded into memory.")

    yield

    logger.info("Shutting down RAG Internship Matching System.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade semantic internship matching system using Sentence Transformers "
        "and FAISS vector embeddings for the Infosys Springboard Virtual Internship Program 7.0."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local frontends, application tracking UI, and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(health_router)
app.include_router(matching_router)


@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
