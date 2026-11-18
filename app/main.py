"""Main FastAPI application entry point for the Unified RAG Internship Matching System.

Fully integrates all 9 VIP 7.0 system modules:
1. Student Profile & Resume Management (Auth, JWT, Session Rotation, Profiles)
2. Resume Parsing & Skill Extraction (PDF, DOCX, Auto-extraction)
3. Internship Knowledge Base & RAG Indexing (55 Opportunities, FAISS)
4. Job-Resume Matching & Compatibility Scoring Agent (Cosine + Coverage)
5. Skill Gap Analysis & Recommendation Agent (Matched vs Missing skills)
6. Cover Letter & Customization Agent (Tailored generation + ATS Score)
7. Interview Preparation & Question Generation Agent (Technical + Behavioral)
8. Application Tracking & Management (State machine lifecycle)
9. Conversational Career Assistant (RAG Chatbot with Safety Guardrails)
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes.health_routes import router as health_router
from app.routes.matching_routes import router as matching_router
from app.routes.platform_routes import router as platform_router
from app.routes.auth_routes import router as auth_router
from app.routes.resume_routes import router as resume_router
from app.routes.interview_routes import router as interview_router
from app.services.vector_store import vector_store

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag_internship_matching")

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes database schema, verifies upload folders, and loads the FAISS
    vector index into memory on startup.
    """
    logger.info("Initializing Unified Internship Assistant System...")

    # Initialize SQLite/PostgreSQL tables automatically
    try:
        init_db()
        logger.info("Database initialized successfully (Users, Tokens, Resumes, Profiles, Applications).")
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")

    # Ensure uploads folder exists
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    # Auto-build vector store if missing on disk (e.g. fresh cloud deployment)
    if not (settings.faiss_index_file.exists() and settings.metadata_file.exists()):
        logger.info("FAISS vector index not found on disk. Auto-building index on startup...")
        try:
            from scripts.build_vector_database import build_and_save_vector_database
            build_and_save_vector_database()
        except Exception as e:
            logger.error(f"Failed to auto-build vector database on startup: {e}", exc_info=True)

    # Load vector store into memory
    loaded = vector_store.load_vector_index()
    if loaded:
        logger.info(f"Vector database ready: {vector_store.get_total_indexed()} internships loaded.")
    else:
        logger.warning("Vector database could not be loaded into memory.")

    yield

    logger.info("Shutting down Unified Internship Assistant System.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Unified Full-Stack AI Internship Platform for Infosys Springboard VIP 7.0.\n\n"
        "Modules Included:\n"
        "1. Student Profile & Resume Management (JWT Auth, Bcrypt, Profiles)\n"
        "2. Resume Parsing & Skill Extraction (PDF/DOCX Extraction)\n"
        "3. Internship Knowledge Base & RAG Indexing (FAISS 384-dim Index)\n"
        "4. Job-Resume Matching & Compatibility Scoring (Cosine Similarity & RAG)\n"
        "5. Skill Gap Analysis & Recommendation Agent\n"
        "6. Resume & Cover Letter Customization Agent (ATS Scoring)\n"
        "7. Interview Preparation & Question Generation Agent\n"
        "8. Application Tracking & Management (Status Lifecycle)\n"
        "9. Conversational Career Assistant (AI Chatbot with Guardrails)"
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
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(matching_router)
app.include_router(platform_router)
app.include_router(interview_router)


@app.get("/", summary="Web Application Portal")
def serve_portal():
    """Serve the unified interactive web portal."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return RedirectResponse(url="/docs")


@app.get("/portal", include_in_schema=False)
def portal_redirect():
    """Alternative route for the web application portal."""
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
