<div align="center">

# 🚀 AI Career Companion
### Unified RAG Career Intelligence Platform & Autonomous Interview Preparation Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=for-the-badge&logo=render&logoColor=white)](https://ai-career-companion-mg65.onrender.com)
[![Swagger API Docs](https://img.shields.io/badge/Swagger-API%20Docs-blue?style=for-the-badge&logo=fastapi&logoColor=white)](https://ai-career-companion-mg65.onrender.com/docs)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/U-ARUN07/ai-career-companion)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.x-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5.x-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![Groq Cloud](https://img.shields.io/badge/Groq%20Cloud-LLaMA--3.3%2070B-F55036.svg?logo=openai&logoColor=white)](https://groq.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)

<p align="center">
  <strong>An enterprise-grade, end-to-end Career Intelligence Suite built for students, graduates, and interns across all disciplines—Computer Science, Chemical, Mechanical, Civil, Electrical, Marketing, Finance, and Human Resources.</strong>
</p>

</div>

---

## 🌐 Live Production Deployment

| Service | Access Link | Description |
| :--- | :--- | :--- |
| 🚀 **Live Web Application** | **[https://ai-career-companion-mg65.onrender.com](https://ai-career-companion-mg65.onrender.com)** | Complete responsive Single Page Application (SPA) |
| 📖 **Interactive Swagger Docs** | **[https://ai-career-companion-mg65.onrender.com/docs](https://ai-career-companion-mg65.onrender.com/docs)** | Interactive OpenAPI test console for all endpoints |
| 💻 **GitHub Repository** | **[https://github.com/U-ARUN07/ai-career-companion](https://github.com/U-ARUN07/ai-career-companion)** | Verified source code & architecture |

> 🔑 **Demo Student Login Credentials:**  
> • **Email:** `arun.student@example.com`  
> • **Password:** `Student123!`

---

## 🏛️ System Architecture

```
                                  +------------------------------------+
                                  |    Client Browser (React 18 UI)    |
                                  |  Web Speech API / Responsive SPA   |
                                  +-----------------+------------------+
                                                    | (REST / JSON)
                                                    v
                                  +------------------------------------+
                                  |      FastAPI Gateway (Uvicorn)     |
                                  |    JWT Auth / CORS / Static SPA    |
                                  +-----------------+------------------+
                                                    |
          +-----------------------+-----------------+-----------------------+
          |                       |                 |                       |
          v                       v                 v                       v
+-------------------+   +-------------------+   +-------------------+   +-------------------+
|  Deep ATS Parser  |   |  RAG Vector Radar |   |  Interview Agent  |   |  CV PDF Architect |
|  PyMuPDF / docx   |   | FAISS Cosine Sim  |   | Groq LPU + Guard  |   | ReportLab Engine  |
+-------------------+   +-------------------+   +-------------------+   +-------------------+
          |                       |                 |                       |
          +-----------------------+-----------------+-----------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |        SQLite Canonical DB         |
                                  |    Users / Profiles / Resumes      |
                                  +------------------------------------+
```

---

## 💎 8 Autonomous Intelligence Modules

| Module | Route | Capabilities & Deliverables |
| :---: | :--- | :--- |
| **01** | `/profile` | **Student Academic & Career Profile**<br/>Central Talent DNA, contact info, university history, verified skills, and multi-resume selector. Strictly preserves candidate identity without overwriting account credentials. |
| **02** | `/resume-parser` | **Deep ATS Resume Parser & Structural Audit**<br/>Multi-format ingestion (`PDF`, `DOCX`, `TXT`), section-aware parsing, skill extraction matrix, quantitative bullet analysis, and real-time 0–100% ATS scoring. |
| **03** | `/knowledge-base` | **Curated Internship Opportunities Radar**<br/>Verified catalog of 22+ multi-domain internships (Chemical, Mechanical, Civil, IT, Finance, Marketing, HR) with verified stipends and 1-click domain filters. |
| **04** | `/job-matching` | **Semantic RAG Matching & Compatibility Radar**<br/>FAISS-dense vector embeddings (`all-MiniLM-L6-v2`) computing cosine similarity against active resumes with explainable match breakdowns. |
| **05** | `/skill-gap` | **Skill Gap Diagnostics & 6-Week Sprints**<br/>Target role gap analysis displaying critical vs secondary skill deficiencies, curated course recommendations, and portfolio project blueprints. |
| **06** | `/customizer` | **Role-Specific CV & Cover Letter Architect**<br/>Interactive bullet tailor, customized cover letters, and **1-Click Executive PDF Generation** powered by Python's `reportlab.platypus` (Modern, Classic, Minimal). |
| **07** | `/interview-prep` | **Technical & Behavioral Mock Simulator**<br/>Role-specific technical problems and STAR behavioral scenarios with automated answer grading (0–10 rubric) and speech feedback. |
| **08** | `/career-assistant` | **Conversational AI Career Copilot & Prep Agent**<br/>Full-mode studio & floating copilot with multi-resume dynamic adaptation, document-grounded Q&A, hands-free voice dictation, and complete session history export. |

---

## ⚡ Key Highlights & Assignment Features

### 1. Resume-Based Role Recommendation
The agent analyzes the candidate's extracted resume components (skills, degree, projects, coursework) and answers queries like:
* *"Which role can I apply for?"*
* *"Which internship is suitable for my skills?"*
* *"What are my strongest technical skills?"*

### 2. Role-Specific Interview Preparation
Generates grounded interview preparation packages tailored to whichever resume is active:
* **Technical Questions:** Specific to the candidate's discipline (McCabe-Thiele for Chemical, Distributed Systems for CS, HVAC for Mechanical).
* **HR & Behavioral:** Formatted in the structured **STAR Framework** (Situation, Task, Action, Result).
* **Interview Roadmap:** Structured 4-week preparation timeline and priority topic checklists.

### 3. Document-Based Q&A (PDF & DOCX)
* Upload any external PDF or DOCX file (e.g. syllabus, job description, study guide).
* System extracts text, grounds the AI in the document context, and answers questions with verified citations.

### 4. Dynamic Multi-Resume Adaptation
* Instant 1-click switching between different resume versions (e.g., Computer Science vs. Chemical Engineering).
* Seamlessly recalculates recommendations across all modules and copilot without page reloads.

### 5. Strict Out-of-Scope Guardrails
* The AI strictly focuses on career guidance, technical preparation, resume analysis, and platform features.
* Off-topic prompts are politely deflected with a guided redirect back to the platform's career tools.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend UI** | React 18, Vite, React Router v7, ReactMarkdown, Remark-GFM, Axios, Modern Vanilla CSS |
| **Speech Engine** | Browser Native Web Speech API (Hands-Free Dictation & Listen Aloud Text-to-Speech) |
| **Backend API** | FastAPI (Python 3.10+), Uvicorn, Pydantic v2, Python-Multipart |
| **AI / LLM** | Groq Cloud API (`qwen/qwen3.8-27b`, LLaMA-3.3 70B) + Multi-Domain Offline Fallback Engine |
| **Document Processing** | PyMuPDF (`fitz`), Python-Docx, PyPDF, ReportLab Platypus |
| **Vector Search & RAG** | Scikit-learn Cosine Similarity, Sentence-Transformers Embedding vectors |
| **Database & ORM** | SQLite3, SQLAlchemy ORM with absolute canonical path resolution |
| **Hosting & CI/CD** | Render.com Web Service (Continuous Deployment from GitHub `main` branch) |

---

## 🚀 Quick Start / Local Setup

### Option A: 1-Click Launch (Windows)
Double-click the included batch launcher in the root directory:
```powershell
.\run.bat
```
*Automatically clears ports 8001 & 5173, starts the FastAPI backend, launches the React frontend, and opens your browser.*

---

### Option B: Manual Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/U-ARUN07/ai-career-companion.git
cd ai-career-companion
```

#### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
*API documentation will be live at: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)*

#### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
*Open [http://localhost:5173](http://localhost:5173) in your browser.*

---

## 🔌 API Reference Highlights

| Method | Endpoint | Description | Auth Required |
| :---: | :--- | :--- | :---: |
| `GET` | `/health` | Uptime monitor health check | No |
| `POST` | `/auth/login` | Authenticate user & return JWT token | No |
| `GET` | `/api/profile/me` | Fetch active student profile & resume meta | Yes |
| `POST` | `/resumes/upload` | Upload & extract structured resume data | Yes |
| `POST` | `/resumes/{id}/set-active` | Set primary active resume | Yes |
| `POST` | `/api/assistant/chat` | AI Career Companion conversational chat | Yes |
| `POST` | `/api/assistant/role-recommendations` | Resume-grounded role matches | Yes |
| `POST` | `/api/assistant/interview-prep` | Role-specific technical & HR prep pack | Yes |
| `POST` | `/api/assistant/upload-doc` | Upload PDF/DOCX for document Q&A | Yes |
| `POST` | `/api/customization/download-cv-pdf` | Generate high-res executive CV PDF | Yes |

---

## 📁 Repository Directory Structure

```
ai-career-companion/
├── 📂 backend/               # FastAPI Python Backend Service
│   ├── 📂 app/               # Core application logic
│   │   ├── 📂 models/        # SQLAlchemy database models
│   │   ├── 📂 routers/       # REST API endpoints (Auth, Resume, Assistant, CV, etc.)
│   │   ├── 📂 schemas/       # Pydantic validation schemas
│   │   ├── 📂 services/      # Groq LLM, ReportLab PDF, NLP & RAG matching
│   │   ├── 📂 utils/         # JWT auth & bcrypt password security
│   │   ├── config.py         # App configuration & absolute DB pathing
│   │   ├── database.py       # SQLAlchemy session & SQLite connection engine
│   │   └── main.py           # FastAPI entry point & CORS configuration
│   ├── 📂 tests/             # Automated test suite (test_all_8_modules.py)
│   ├── 📂 uploads/           # Ephemeral storage for uploaded resumes & CVs
│   ├── app.db                # Canonical SQLite database (6 users, 22 internships)
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
│
├── 📂 frontend/              # React 18 + Vite Web Application
│   ├── 📂 dist/              # Production-compiled bundle served directly by backend
│   ├── 📂 public/            # Static assets and icons
│   ├── 📂 src/
│   │   ├── 📂 components/    # Reusable widgets (Sidebar, Layout, FloatingAICopilot)
│   │   ├── 📂 pages/         # 8 Intelligence Suite views (Auth, Dashboard, Assistant)
│   │   ├── 📂 services/      # Axios HTTP client with JWT interceptor
│   │   ├── App.css           # Styling, themes, responsive layout, animations
│   │   └── App.jsx           # Client-side routing and protected routes
│   ├── package.json          # Node dependencies & build scripts
│   ├── vercel.json           # SPA rewrite configuration
│   └── vite.config.js        # Vite dev server & backend reverse-proxy
│
├── 📄 main.py                # Root server entry point for Render production deployment
├── 📄 render.yaml            # Render infrastructure-as-code blueprint
├── 📄 run.bat                # 1-Click launcher for Windows
├── 📄 run.ps1                # PowerShell launcher script
├── 📄 PROJECT_SUMMARY.md     # In-depth module-by-module architectural breakdown
├── 📄 LICENSE                # Open-source MIT License
└── 📄 README.md              # Project documentation
```

---

## 👨‍💻 Author & Acknowledgments

* **Candidate:** Arun
* **Mentor:** Vijay Parmar
* **Program:** Infosys Springboard Virtual Internship Program 7.0
* **Project Title:** AI Career Companion Agent for Internship Matching and Interview Preparation

---

<div align="center">
  <sub>Built with ❤️ for ambitious students and job seekers worldwide.</sub>
</div>
