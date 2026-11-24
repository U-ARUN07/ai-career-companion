# AI Career Companion: Project Summary & Architecture Overview

## Overview
- **Project Name**: AI Career Companion: Intelligent Internship Matching, ATS Resume Scoring & Interview Preparation Platform
- **Program**: Infosys Springboard Virtual Internship Program 7.0
- **Working Directory**: `C:\infosys Internship\AI Career Companion`
- **Frontend**: React 18 + Vite (Tailwind CSS, Lucide icons, Axios, Web Speech API) running on `http://localhost:5173`
- **Backend**: FastAPI Python Backend (Uvicorn) running on `http://127.0.0.1:8001`
- **LLM Engine**: Groq Cloud API (`qwen/qwen3.8-27b`) with automatic fallback to `openai/gpt-oss-120b`
- **Document Generation**: Python `reportlab.platypus` for 1-Click CV PDF generation
- **Test Suite**: 9 passing test cases in `backend/tests/test_all_8_modules.py` (100% pass rate)

---

## 8 Core Modules Implemented

### Module 1: Student Profile and Resume Management
- **Routes**: `/profile`, `GET /api/profile/me`, `PUT /api/profile/me`, `GET /resumes/my`, `POST /resumes/upload`
- **Features**: User authentication with JWT bearer tokens, profile personalization (target role, university, technical skills), and active resume storage.

### Module 2: Resume Parsing and Skill/Experience Extraction
- **Routes**: `/resume-parser`, `POST /api/documents/upload`
- **Features**: Multi-format document parser (`PyMuPDF`, `python-docx`, `pypdf`) extracting personal info, technical skills, developer tools, soft skills, experience, projects, education, and career recommendations via Groq.

### Module 3: Internship Knowledge Base with RAG Retrieval
- **Routes**: `/knowledge-base`, `GET /api/knowledge-base/internships`, `GET /api/knowledge-base/domains`, `POST /api/knowledge-base/rag-query`
- **Features**: Verified catalog across 12+ domains with real-time grounded RAG question answering, verified citations, and stipend/work-mode filters.

### Module 4: Job-Resume Matching and Compatibility Scoring
- **Routes**: `/job-matching`, `GET /matching/compatibility`
- **Features**: Semantic matching against active resume profile, compatibility scoring (0-100%), matched vs missing skills breakdown, and grounded retrieval explanations.

### Module 5: Skill Gap Analysis and Improvement Recommendations
- **Routes**: `/skill-gap`, `GET /api/skill-gap/roles`, `POST /api/skill-gap/analyze`
- **Features**: Role-specific gap analysis with match %, critical & secondary skill gaps, structured 6-week learning roadmap, recommended online courses, and resume-ready portfolio projects.

### Module 6: Role-specific Resume and Cover Letter Customization
- **Routes**: `/customizer`, `POST /api/customization/tailor-resume`, `POST /api/customization/generate-cover-letter`, `POST /api/customization/download-cv-pdf`
- **Features**: Tailored resume bullet points and ATS keywords, personalized cover letters with tone selection, and **1-Click Executive CV PDF Generator** (Modern, Classic, Minimal templates).

### Module 7: Interview Preparation with Role-specific Questions & Strategies
- **Routes**: `/interview-prep`, `GET /api/interview/roles`, `GET /api/interview/questions`, `POST /api/interview/evaluate-answer`
- **Features**: Role-specific technical & behavioral STAR questions with answering strategies, mock answer practice, and Groq AI Answer Evaluator with score /10, strengths, and model responses.

### Module 8: Conversational Career Assistant for Ongoing Guidance
- **Routes**: `/career-assistant`, `POST /api/assistant/chat`, `POST /api/export/chat`
- **Features**: Context-aware career chatbot grounded in the student's active resume, Web Speech voice dictation, multi-format export (PDF, Word DOCX, TXT), and Floating AI Copilot widget across all views.

---

## ⚡ 1-Click Execution

- **VS Code**: Press `Ctrl + Shift + B` (executes `run.ps1`, clears ports, starts backend & frontend, opens browser).
- **Batch Launcher**: Double-click `run.bat`.
- **Manual Launch**:
  1. Backend: `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
  2. Frontend: `cd frontend && npm run dev`
  3. Open: `http://localhost:5173`
- **Run Verification Tests**:
  `cd backend && python -m pytest tests/test_all_8_modules.py`
