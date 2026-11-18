# IntelliIntern AI: Project Handover & Complete System State

## Overview
- **Project Name**: IntelliIntern AI: Unified RAG Career Intelligence Platform
- **Program**: Infosys Springboard Virtual Internship Program 7.0
- **Working Directory**: `C:\infosys Internship\IntelliIntern AI - Unified RAG Career Intelligence Platform`
- **Candidate Name**: Configurable via Profile / UI (Default demo: Arun)
- **Database**: Zero-config SQLite (`app.db`), auto-migrated on startup; supports PostgreSQL if `DATABASE_URL` is configured.
- **LLM Engine**: High-Speed Groq Cloud API integrated (`qwen/qwen3.8-27b`) via `.env` (`GROQ_API_KEY`).
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Vector Index**: FAISS IndexFlatIP with 55 synthetic internship opportunities in `vector_store/`
- **Test Suite**: 30 passing unit/integration tests with 100% pass rate (`python -m pytest`)

---

## ⚡ Groq Cloud AI Engine Integration (Full Coverage)

Groq high-speed inference powers all intelligent tasks across the platform:
1. **Conversational Career Companion** (`app/services/chatbot_service.py`):
   - Grounded RAG synthesis with strict safety guardrails and anti-hallucination boundary checks.
2. **Tailored Cover Letter Generation** (`app/services/cover_letter_service.py`):
   - High-accuracy 3-paragraph tailored cover letters dynamically highlighting candidate projects and skills.
   - ATS Compatibility Scoring (0-100%) and keyword suggestions.
3. **Grounded Matching Rationales** (`app/services/explanation_service.py`, `app/services/matching_service.py`):
   - High-speed JSON explanations generated concurrently via `ThreadPoolExecutor` for low latency (~1.5s total).
4. **Dynamic Interview Question Generation** (`app/services/interview_service.py`):
   - 5 role-specific questions across Core Technical, Domain, Algorithmic, Behavioral, and Fit categories.
5. **Interview Mock Practice Evaluation** (`app/services/interview_service.py`):
   - AI rubric grading assessing score (0-100), key strengths, actionable recommendations, and STAR method compliance.

*Graceful Fault-Tolerance: Every Groq-powered task includes deterministic rule-based fallback logic, ensuring continuous operation even offline or during network disruptions.*

---

## 9 Unified Modules Implemented

1. **Student Profile and Resume Management**:
   - `app/routes/auth_routes.py`, `app/models.py`, `app/security.py`, `app/crud.py`
   - User registration (`POST /auth/register`), login (`POST /auth/login`), JWT access & refresh tokens with rotation (`POST /auth/refresh`), profile management (`GET/PUT /auth/profile`), protected user info (`GET /auth/me`).

2. **Resume Parsing and Skill Extraction**:
   - `app/services/resume_parser.py`, `app/routes/resume_routes.py`
   - Ingests PDF (`PyMuPDF`) and DOCX (`python-docx`), extracts structured candidate fields (Skills, Education, Projects, Experience).
   - Direct 1-click upload and match: `POST /resume/upload-and-match`.

3. **Internship Knowledge Base and RAG Indexing**:
   - `data/internships.json` (55 curated opportunities across 13 domains).
   - `vector_store/faiss_index.bin` and `vector_store/internships_metadata.json`.

4. **Job-Resume Matching and Compatibility Scoring Agent**:
   - `app/services/matching_service.py`, `app/routes/matching_routes.py`
   - Cosine similarity matching against 384-dimensional dense vectors with requirement coverage score and anti-hallucination explanations.

5. **Skill Gap Analysis and Recommendation Agent**:
   - `app/services/explanation_service.py`
   - Analyzes matched vs missing skills and produces structured learning roadmaps.

6. **Resume and Cover Letter Customization Agent**:
   - `app/services/cover_letter_service.py`, `app/routes/platform_routes.py`
   - Generates tailored cover letters powered by Groq LLM with ATS Compatibility Score (0-100%) and keyword suggestions.

7. **Interview Preparation and Question Generation Agent**:
   - `app/services/interview_service.py`, `app/routes/interview_routes.py`
   - Generates 5 tailored technical, domain, and behavioral interview questions with scoring rubrics and mock answer evaluation (`POST /api/v1/interview/questions`, `POST /api/v1/interview/evaluate`).

8. **Application Tracking and Management**:
   - `app/services/application_service.py`, `app/routes/platform_routes.py`
   - Status progression: Applied → Under Review → Interview Scheduled → Offer.

9. **Conversational Career Assistant**:
   - `app/services/chatbot_service.py`, `app/routes/platform_routes.py`
   - RAG-powered chatbot with strict safety guardrails and Groq LLM synthesis (`POST /api/v1/assistant/chat`).

---

## Quick Execution

- **VS Code**: Press `Ctrl + Shift + B` (runs `run.ps1`, frees port 8000, opens browser).
- **Batch Script**: Double-click `run.bat`.
- **Manual Command**: `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- **Web Portal**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Tests**: `python -m pytest` (30/30 passed, 100% pass rate)
