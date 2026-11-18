# Unified AI Internship Matching & Career Assistant System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![FAISS](https://img.shields.io/badge/FAISS-CPU_1.16%2B-green.svg)](https://github.com/facebookresearch/faiss)
[![Sentence--Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

### 🚀 1-Click Launch & Quick Access Buttons

| Action | One-Click Button | Direct Link |
| :--- | :--- | :--- |
| **Launch Web Portal** | [![Open Local App](https://img.shields.io/badge/🚀_Open_Live_Portal-http%3A%2F%2Flocalhost%3A8000-007acc?style=for-the-badge)](http://localhost:8000) | [http://localhost:8000](http://localhost:8000) |
| **Interactive API Docs** | [![Open Swagger Docs](https://img.shields.io/badge/📖_Swagger_API_Docs-http%3A%2F%2Flocalhost%3A8000%2Fdocs-009688?style=for-the-badge)](http://localhost:8000/docs) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Deploy to Cloud (Free)** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/U-ARUN07/rag-internship-matching) | [Deploy on Render](https://render.com/deploy?repo=https://github.com/U-ARUN07/rag-internship-matching) |

> 💡 *Clicking the blue **Open Live Portal** button immediately opens `http://localhost:8000` in your browser.*

---

## 📌 Executive Summary

Engineered as a single, unified full-stack platform for the **Infosys Springboard Virtual Internship Program 7.0**, this system unifies all planned academic milestones and modules into a cohesive production application:

1. **Student Profile and Resume Management**: User registration, login, JWT access & refresh tokens with token rotation, bcrypt password hashing, and customizable student profiles.
2. **Resume Parsing and Skill Extraction**: Native document parser ingesting PDF (`PyMuPDF`) and DOCX (`python-docx`), extracting skills, education, and projects.
3. **Internship Knowledge Base and RAG Indexing**: 55 curated synthetic internship opportunities across 13 domains indexed into a 384-dimensional FAISS vector database.
4. **Job-Resume Matching and Compatibility Scoring Agent**: Semantic dense vector search with cosine similarity scoring and grounded anti-hallucinatory explanations.
5. **Skill Gap Analysis and Recommendation Agent**: Identifies matched vs missing technical skills and generates customized learning roadmaps.
6. **Resume and Cover Letter Customization Agent**: Generates professional, company-specific cover letters with ATS Compatibility Scoring and keyword suggestions.
7. **Interview Preparation and Question Generation Agent**: Generates 5 tailored technical, algorithmic, and behavioral interview questions with scoring rubrics and mock practice feedback.
8. **Application Tracking and Management**: Application submission, status lifecycle management (*Applied*, *Under Review*, *Interview Scheduled*, *Offer*), and cover letter archiving.
9. **Conversational Career Assistant**: RAG-powered chatbot with strict safety guardrails preventing out-of-scope queries.

---

## 🏗️ Unified Architecture

```mermaid
flowchart TD
    subgraph Data_Layer ["1. Persistence & Vector Index Layer"]
        DB[("app.db (SQLite / PostgreSQL)\nUsers, Resumes, Profiles, Apps")]
        FS[("vector_store/faiss_index.bin\n55 Indexed Internships (384-dim)")]
        UP[("uploads/resumes/\nStored PDF & DOCX Files")]
    end

    subgraph Core_Services ["2. AI & Processing Services"]
        AUTH["Security & Token Service\n(Bcrypt + JWT HS256)"]
        PARSE["Resume Parser\n(PyMuPDF + docx + Heuristics)"]
        VEC["Vector Store & Embeddings\n(SentenceTransformers all-MiniLM-L6-v2)"]
        MATCH["Matching & Explanation Service\n(Cosine Similarity + RAG)"]
        CL["Cover Letter & ATS Agent"]
        INT["Interview Prep Coach Agent"]
        CHAT["Conversational Career Assistant\n(Safety Guardrails)"]
    end

    subgraph API_Routers ["3. FastAPI Endpoints"]
        R_AUTH["/auth (register, login, refresh, me, profile)"]
        R_RES["/resume (upload, download, upload-and-match)"]
        R_MATCH["/api/v1/matching (match, internships)"]
        R_EXT["/api/v1 (cover-letter, applications, chat)"]
        R_INT["/api/v1/interview (questions, evaluate)"]
    end

    subgraph Web_UI ["4. Frontend & User Interface"]
        UI["Unified Web Portal\n(http://localhost:8000)"]
    end

    Data_Layer --> Core_Services
    Core_Services --> API_Routers
    API_Routers --> UI
```

---

## ⚡ How to Run Locally

### Option 1: VS Code Shortcut (Recommended)
Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd> in VS Code.
- Automatically frees port 8000 if occupied.
- Starts the server and opens `http://localhost:8000` in your browser.

### Option 2: 1-Click Batch Script
Double-click `run.bat` (or in terminal: `.\run.bat`).
- Automatically checks port 8000, starts `uvicorn`, and launches your browser.

### Option 3: Manual Terminal Command
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open **http://localhost:8000** in your browser.

---

## 🧪 Comprehensive Verification Suite

Run all 30 unit, integration, and platform test cases:
```powershell
python -m pytest
```
*Current Result: 30 Passed (100% Pass Rate).*

---

## 👥 Candidate & Project Metadata

- **Internship Program**: Infosys Springboard Virtual Internship Program 7.0
- **Candidate Name**: **Arun**
- **Repository**: [https://github.com/U-ARUN07/rag-internship-matching](https://github.com/U-ARUN07/rag-internship-matching)
- **Zero Configuration**: Runs with zero manual setup via bundled SQLite database and pre-indexed FAISS vectors.
