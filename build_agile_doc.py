import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:insideV w:val="none"/></w:tblBorders>')
    tblPr.append(borders)

def add_heading_styled(doc, text, level, space_before=14, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.bold = True
    
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(15, 30, 80) # Navy
        # Add bottom border or line
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(20, 60, 120)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(40, 80, 140)
    return p

def add_body_p(doc, text="", bold_prefix="", space_after=4, bullet=False):
    if bullet:
        p = doc.add_paragraph(style='List Bullet')
    else:
        p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
        
    if text:
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def format_table(table, col_widths, headers, data, header_bg="1E3A8A"):
    set_table_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=180, right=180)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(9.5)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data rows
    for r_idx, row_data in enumerate(data):
        row = table.add_row()
        cells = row.cells
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cells[c_idx].text = str(val)
            set_cell_background(cells[c_idx], bg_color)
            set_cell_margins(cells[c_idx], top=100, bottom=100, left=180, right=180)
            cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cells[c_idx].paragraphs[0]
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(51, 65, 85)
                if c_idx == 0 or (c_idx == len(row_data)-1 and str(val) in ["Done", "Pass", "High"]):
                    run.bold = True
                    if str(val) in ["Done", "Pass"]:
                        run.font.color.rgb = RGBColor(16, 120, 60) # Green
                    elif str(val) == "High":
                        run.font.color.rgb = RGBColor(180, 40, 40) # Crimson

    # Column widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def build_full_documentation():
    doc = docx.Document()
    
    # Page setup - A4
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # --------------------------------------------------------------------------
    # COVER PAGE
    # --------------------------------------------------------------------------
    p_cov_top = doc.add_paragraph()
    p_cov_top.paragraph_format.space_before = Pt(36)
    p_cov_top.paragraph_format.space_after = Pt(8)
    r_org = p_cov_top.add_run("INFOSYS SPRINGBOARD VIRTUAL INTERNSHIP PROGRAM 7.0")
    r_org.font.name = "Arial"
    r_org.font.size = Pt(11)
    r_org.bold = True
    r_org.font.color.rgb = RGBColor(0, 102, 179) # Infosys Blue

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("AI Career Companion")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(28)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(15, 30, 80)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(28)
    r_sub = p_sub.add_run("Unified RAG Career Intelligence & Internship Matching Platform\nAgile Project Documentation & Comprehensive Technical Report")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Decorative Box / Metadata Table on Cover
    cov_table = doc.add_table(rows=5, cols=2)
    cov_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cov_data = [
        ("Project Title:", "AI Career Companion (Unified RAG Career Intelligence Platform)"),
        ("Prepared By:", "Arun (Candidate / Intern)"),
        ("Project Duration:", "October 2026 – November 2026"),
        ("Program Track:", "Artificial Intelligence & RAG Career Intelligence"),
        ("Project Mentor:", "Vijay Parmar")
    ]
    set_table_borders(cov_table, color="CBD5E1", sz="4")
    for idx, (label, val) in enumerate(cov_data):
        row = cov_table.rows[idx]
        row.cells[0].text = label
        row.cells[1].text = val
        set_cell_background(row.cells[0], "F1F5F9")
        set_cell_background(row.cells[1], "FFFFFF")
        set_cell_margins(row.cells[0], top=120, bottom=120, left=160, right=160)
        set_cell_margins(row.cells[1], top=120, bottom=120, left=160, right=160)
        row.cells[0].paragraphs[0].runs[0].font.name = "Arial"
        row.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(30, 41, 59)
        row.cells[1].paragraphs[0].runs[0].font.name = "Arial"
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(10)
        row.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(15, 23, 42)
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.07)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # INDEX / TABLE OF CONTENTS
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "Page 2: Index", 1, space_before=12, space_after=12)
    
    index_headers = ["No.", "Section Name", "Page Reference"]
    index_data = [
        ["1", "Project Overview", "3"],
        ["2", "Project Objective", "4"],
        ["3", "Technology Stack", "5"],
        ["4", "Project Requirements (Functional & Non-Functional)", "6"],
        ["5", "System Architecture & End-to-End Workflow", "7"],
        ["6", "Product Backlog (User Stories & Epics)", "8"],
        ["7", "Sprint Planning & Timeline Breakdown", "9"],
        ["8", "Sprint Tasks & Execution Status", "10"],
        ["9", "Implementation & Detailed Key Modules (8 Modules)", "11"],
        ["10", "Testing Strategy & Comprehensive Test Results", "13"],
        ["11", "Challenges Encountered & Engineering Solutions", "14"],
        ["12", "Final Project Status, Live Deliverables & Access Credentials", "15"],
        ["Appendix", "10-Slide Project Presentation Script", "16"]
    ]
    idx_tbl = doc.add_table(rows=1, cols=3)
    format_table(idx_tbl, [0.8, 4.27, 1.2], index_headers, index_data, header_bg="0F172A")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 1: PROJECT OVERVIEW
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "1. Project Overview", 1)
    
    add_heading_styled(doc, "1.1 Project Name", 2)
    add_body_p(doc, "AI Career Companion — Unified RAG Career Intelligence Platform", bold_prefix="Official Title: ")
    
    add_heading_styled(doc, "1.2 What is the Project?", 2)
    add_body_p(doc, "AI Career Companion is a production-ready, full-stack career intelligence system designed to revolutionize how students and internship seekers transition from academia into technical industries. The platform integrates eight cohesive modules that automate ATS-grade resume parsing, provide semantic internship matching through Retrieval-Augmented Generation (RAG), run mathematical skill gap diagnostics, generate role-tailored cover letters and resumes, simulate real-time AI voice/text mock interviews with STAR-method feedback, and offer 24/7 conversational career copilot guidance.")

    add_heading_styled(doc, "1.3 Problem Statement", 2)
    add_body_p(doc, "College graduates and internship candidates face systemic hurdles in the modern employment landscape:")
    add_body_p(doc, "Traditional job boards require candidates to sift through hundreds of irrelevant listings without understanding their true fit.", bullet=True, bold_prefix="Fragmented Internship Discovery: ")
    add_body_p(doc, "Over 75% of candidate resumes are filtered out by automated Applicant Tracking Systems due to keyword mismatches and layout parsing errors.", bullet=True, bold_prefix="The ATS 'Black Box': ")
    add_body_p(doc, "Students receive binary rejections without actionable diagnostic feedback on exactly what technical skills or certifications they lack.", bullet=True, bold_prefix="Invisible Skill Deficits: ")
    add_body_p(doc, "Generic interview coaching fails to simulate authentic company and role-specific technical questions or provide instant objective evaluation.", bullet=True, bold_prefix="Superficial Interview Preparation: ")

    add_heading_styled(doc, "1.4 Target Users", 2)
    add_body_p(doc, "The platform is engineered to serve the following primary stakeholders:")
    add_body_p(doc, "College and university students looking for tailored technical internships and real-world placement guidance.", bullet=True, bold_prefix="Internship Candidates & Students: ")
    add_body_p(doc, "Counselors tracking student readiness, resume health, and industry competency benchmarks.", bullet=True, bold_prefix="University Placement Cells & Academic Mentors: ")
    add_body_p(doc, "HR teams seeking qualified candidate profiles ranked by objective vector similarity and verifiable skills.", bullet=True, bold_prefix="Corporate Talent Acquisition Teams: ")
    add_body_p(doc, "Supervisors assessing project milestones, code execution, and system architecture.", bullet=True, bold_prefix="Project Evaluators & Industry Reviewers: ")

    # --------------------------------------------------------------------------
    # SECTION 2: PROJECT OBJECTIVE
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "2. Project Objective", 1)
    add_body_p(doc, "The overarching mission of the project is to build an intelligent, transparent, and automated career acceleration pipeline for aspiring interns. The core engineering objectives achieved include:")
    
    add_body_p(doc, "Develop an automated extraction pipeline for PDF and DOCX files that extracts contact info, skills, education, projects, and work history into structured JSON schemas.", bullet=True, bold_prefix="1. High-Precision Resume Ingestion: ")
    add_body_p(doc, "Implement ChromaDB vector store with sentence-transformers (all-MiniLM-L6-v2) embeddings to store, index, and retrieve company internship descriptions using semantic similarity.", bullet=True, bold_prefix="2. Semantic RAG Knowledge Retrieval: ")
    add_body_p(doc, "Create a hybrid scoring algorithm combining TF-IDF keyword density and dense vector cosine similarity to eliminate bias and produce explainable compatibility scores.", bullet=True, bold_prefix="3. Dual-Engine Compatibility Scoring: ")
    add_body_p(doc, "Build an algorithmic diagnostic engine that compares candidate resumes against target job descriptions, categorizing deficits into critical, secondary, and recommended learning pathways.", bullet=True, bold_prefix="4. Automated Skill Gap Diagnostics: ")
    add_body_p(doc, "Leverage Groq LLaMA 3.3 70B to rewrite resumes and draft personalized cover letters customized to specific job descriptions.", bullet=True, bold_prefix="5. Context-Aware Application Tailoring: ")
    add_body_p(doc, "Implement voice-enabled mock interviews featuring role-specific questions, speech-to-text recording, and multi-dimensional scoring (relevance, depth, clarity).", bullet=True, bold_prefix="6. Interactive Mock Interview Simulation: ")
    add_body_p(doc, "Deploy a fully operational, cloud-hosted production system on Render with automated CI/CD from GitHub, interactive Swagger documentation, and a dual Light/Dark theme React frontend.", bullet=True, bold_prefix="7. Full Cloud Deployment & CI/CD: ")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 3: TECHNOLOGY STACK
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "3. Technology Stack", 1)
    add_body_p(doc, "The project utilizes a modern, decoupled client-server architecture designed for high throughput, low latency (< 1.5s LLM inference), and cross-platform compatibility:")

    tech_headers = ["Category", "Technology Selected", "Purpose in Architecture"]
    tech_data = [
        ["Programming Language", "Python 3.14 / JavaScript (ES2023)", "Core language for backend AI workflows and frontend reactivity"],
        ["Backend Framework", "FastAPI (Uvicorn ASGI Server)", "High-performance asynchronous REST API backend with automated OpenAPI docs"],
        ["Frontend Framework", "React 19 (Vite Build Tool)", "Modern single-page application with reactive state and instant HMR"],
        ["Design System & Icons", "Plus Jakarta Sans & Lucide React", "Corporate typography, responsive layouts, and unified dual-theme tokens"],
        ["AI / LLM Engine", "Groq Cloud (LLaMA 3.3 70B Versatile)", "Ultra-fast LPU inference (500+ tokens/sec) for RAG reasoning and generation"],
        ["Vector Database", "ChromaDB (Cosine Similarity Collection)", "Persistent vector embeddings storage for dense semantic retrieval"],
        ["Embeddings Model", "Sentence-Transformers (all-MiniLM-L6-v2)", "384-dimensional dense semantic representation of resumes and job listings"],
        ["Relational Database", "SQLite / SQLAlchemy ORM", "Persistent relational store for student profiles, user auth, and saved resumes"],
        ["Authentication", "OAuth2 / JWT (JSON Web Tokens) & Bcrypt", "Stateless, secure token authentication with password hashing"],
        ["Cloud Hosting & CI/CD", "Render Cloud Platform & GitHub Actions", "Continuous deployment pipeline running production Uvicorn web services"],
        ["Availability Monitor", "Cron-Job.org Automated Pinger", "Automated 10-minute health-check polling to ensure 24/7 zero cold starts"],
        ["Version Control", "Git & GitHub", "Source code management, feature branching, and release tracking"]
    ]
    tech_tbl = doc.add_table(rows=1, cols=3)
    format_table(tech_tbl, [1.5, 2.2, 2.57], tech_headers, tech_data, header_bg="1E3A8A")

    # --------------------------------------------------------------------------
    # SECTION 4: PROJECT REQUIREMENTS
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "4. Project Requirements", 1)
    
    add_heading_styled(doc, "4.1 Functional Requirements (FR)", 2)
    add_body_p(doc, "Secure registration, login with JWT tokens, role management, and immutable candidate talent DNA profile persistence.", bullet=True, bold_prefix="FR1 - Authentication & Student Profile: ")
    add_body_p(doc, "Upload and parse PDF/DOCX resumes, extract technical skills, contact details, work history, and calculate ATS readiness score.", bullet=True, bold_prefix="FR2 - Resume Ingestion & Parsing: ")
    add_body_p(doc, "Vectorized repository of 22+ multi-department internships with natural language semantic search and RAG synthesis.", bullet=True, bold_prefix="FR3 - Knowledge Base & Semantic Search: ")
    add_body_p(doc, "Hybrid compatibility scoring (TF-IDF keyword overlap + dense vector cosine similarity) displaying match percentage and gap breakdown.", bullet=True, bold_prefix="FR4 - Job-Resume Compatibility Engine: ")
    add_body_p(doc, "Automated diagnosis of missing technical skills, categorized into critical, secondary, and recommended certifications with actionable courses.", bullet=True, bold_prefix="FR5 - Skill Gap Analysis: ")
    add_body_p(doc, "Generation of job-targeted resumes and persuasive, formal cover letters tailored to specific internship descriptions.", bullet=True, bold_prefix="FR6 - Application Customization: ")
    add_body_p(doc, "Speech-to-text voice dictation, role-specific question generation, response evaluation, and instant STAR-method scorecards.", bullet=True, bold_prefix="FR7 - Interactive AI Interview Simulator: ")
    add_body_p(doc, "Persistent conversational copilot providing real-time career advice, salary estimates, and internship navigation.", bullet=True, bold_prefix="FR8 - 24/7 Conversational Career Assistant: ")

    add_heading_styled(doc, "4.2 Non-Functional Requirements (NFR)", 2)
    add_body_p(doc, "FastAPI asynchronous handlers and Groq LPU inference ensure full LLM responses in under 1.5 seconds.", bullet=True, bold_prefix="NFR1 - Performance & Latency: ")
    add_body_p(doc, "Bcrypt password hashing (12 rounds), stateless JWT tokens with expiry, and strict client-side credential protection.", bullet=True, bold_prefix="NFR2 - Security & Data Protection: ")
    add_body_p(doc, "Decoupled 3-tier architecture with modular APIRouters enabling easy scaling and migration to cloud PostgreSQL.", bullet=True, bold_prefix="NFR3 - Modularity & Scalability: ")
    add_body_p(doc, "Responsive design supporting mobile and desktop, instant Light/Dark theme switching, and 1-click demo autofill.", bullet=True, bold_prefix="NFR4 - Usability & Accessibility: ")
    add_body_p(doc, "24/7 continuous availability enabled via Cron-Job keep-alive pinger preventing free-tier instance sleep.", bullet=True, bold_prefix="NFR5 - High Availability: ")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 5: SYSTEM ARCHITECTURE & WORKFLOW
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "5. System Architecture / Workflow", 1)
    add_body_p(doc, "The system follows an enterprise Multi-Tier Clean Architecture pattern, decoupling user presentation, business logic orchestration, vector storage, and external AI foundation models:")

    add_heading_styled(doc, "5.1 Architectural Tier Breakdown", 2)
    add_body_p(doc, "React 19 SPA with Vite, ThemeContext (Light/Dark mode), Lucide React iconography, and Axios HTTP client with Bearer token interceptors.", bullet=True, bold_prefix="Presentation Tier (Client): ")
    add_body_p(doc, "FastAPI application mounting modular APIRouters (`/auth`, `/resumes`, `/internships`, `/matching`, `/cv`, `/interview`, `/agent`, `/health`).", bullet=True, bold_prefix="API & Application Tier (Backend): ")
    add_body_p(doc, "Encapsulates business rules across AuthService, ResumeParserService, RAGService, MatchingEngine, and InterviewService.", bullet=True, bold_prefix="Service & Logic Tier: ")
    add_body_p(doc, "SQLAlchemy ORM with SQLite database for structured entities alongside ChromaDB vector collection storing 384-dimensional dense embeddings.", bullet=True, bold_prefix="Data & Vector Tier: ")
    add_body_p(doc, "Groq Cloud LPU running LLaMA 3.3 70B Versatile for high-speed deterministic generation and reasoning.", bullet=True, bold_prefix="Inference Engine (LLM): ")

    add_heading_styled(doc, "5.2 End-to-End RAG & Processing Workflow", 2)
    add_body_p(doc, "The core RAG pipeline operates through the following deterministic sequence:")
    add_body_p(doc, "User uploads PDF/DOCX -> PyPDF/docx2txt extracts raw text -> Regex + NLP sanitization.", bold_prefix="1. Ingestion: ", bullet=True)
    add_body_p(doc, "Resume and internship documents are partitioned into semantic chunks with token overlap.", bold_prefix="2. Chunking: ", bullet=True)
    add_body_p(doc, "sentence-transformers/all-MiniLM-L6-v2 transforms chunks into dense 384-d vectors.", bold_prefix="3. Vectorization: ", bullet=True)
    add_body_p(doc, "Embeddings indexed in ChromaDB with metadata (role, skills, department, stipend).", bold_prefix="4. Indexing: ", bullet=True)
    add_body_p(doc, "User prompts/queries are embedded and queried against ChromaDB using cosine distance (Top-k).", bold_prefix="5. Dense Retrieval: ", bullet=True)
    add_body_p(doc, "Retrieved context chunks are combined with system prompts and candidate talent profile.", bold_prefix="6. Context Injection: ", bullet=True)
    add_body_p(doc, "Groq LLaMA 3.3 synthesizes response with strict factual grounding and structured JSON schemas.", bold_prefix="7. LLM Generation: ", bullet=True)

    # --------------------------------------------------------------------------
    # SECTION 6: PRODUCT BACKLOG
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "6. Product Backlog", 1)
    add_body_p(doc, "The project backlog was structured into high-priority epics aligned with the Infosys Springboard VIP 7.0 curriculum:")

    backlog_headers = ["ID", "Epic / Module", "User Story & Description", "Priority", "Status"]
    backlog_data = [
        ["P001", "Core Setup", "Setup FastAPI backend, React Vite frontend, SQLite ORM, and Git repository", "High", "Done"],
        ["P002", "Authentication", "As a student, I want to securely register and log in using JWT tokens", "High", "Done"],
        ["P003", "Student Profile", "As a user, I want to view, edit, and persist my academic profile and talent DNA", "High", "Done"],
        ["P004", "Resume Parser", "As a user, I want to upload PDF/DOCX resumes and extract skills and ATS scores", "High", "Done"],
        ["P005", "Vector RAG Store", "As a system, vectorize 22+ internships into ChromaDB for semantic search", "High", "Done"],
        ["P006", "Job Matching", "As a user, I want to view mathematical match scores between my resume and jobs", "High", "Done"],
        ["P007", "Skill Gap Analysis", "As a student, I want to see missing skills and recommended upskilling roadmaps", "High", "Done"],
        ["P008", "Cover Letter Gen", "As an applicant, I want AI to generate targeted cover letters for specific internships", "Medium", "Done"],
        ["P009", "AI Mock Interview", "As a candidate, I want voice/text mock interviews with real-time STAR evaluation", "High", "Done"],
        ["P010", "Career Copilot", "As a student, I want a 24/7 conversational AI assistant for ongoing career advice", "High", "Done"],
        ["P011", "Cloud Deployment", "Deploy full-stack app on Render cloud with CI/CD and keep-alive monitor", "High", "Done"]
    ]
    backlog_tbl = doc.add_table(rows=1, cols=5)
    format_table(backlog_tbl, [0.6, 1.3, 2.77, 0.8, 0.8], backlog_headers, backlog_data, header_bg="1E3A8A")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 7: SPRINT PLANNING
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "7. Sprint Planning", 1)
    add_body_p(doc, "Development was organized into four focused 2-week Agile sprints covering the 8-week internship lifecycle:")

    sprint_plans = [
        ("Sprint 1: Architecture, Authentication & Talent DNA Profile", "Weeks 1–2", "Establish full-stack project skeleton, database ORM, JWT security, and candidate profile management.", [
            "Initialize repository with clean modular directory layout (backend / frontend).",
            "Configure SQLAlchemy models for User, StudentProfile, Resume, and Internship entities.",
            "Implement OAuth2 Password Bearer flow, bcrypt hashing, and JWT token issuance.",
            "Develop React login, registration, and central student profile view."
        ]),
        ("Sprint 2: Resume Parser Pipeline & ChromaDB Vector Store", "Weeks 3–4", "Build document parsing engine and establish dense vector retrieval knowledge base.", [
            "Implement multi-format text extractor supporting PDF (pypdf) and DOCX (docx2txt).",
            "Build regex + NLP entity extraction for technical skills, certifications, and contact details.",
            "Integrate sentence-transformers and initialize ChromaDB vector collection.",
            "Seed 22 multi-disciplinary internship postings across CS, Data Science, and Engineering."
        ]),
        ("Sprint 3: Matching Engine, Skill Gap Analytics & Cover Letter Tailoring", "Weeks 5–6", "Create the core intelligence layer combining compatibility scoring and gap recommendations.", [
            "Implement hybrid compatibility scoring (TF-IDF keyword overlap + dense cosine similarity).",
            "Build skill gap diagnostic service identifying critical vs secondary skill deficits.",
            "Curate structured upskilling courses and roadmap recommendations.",
            "Implement Groq LLaMA 3.3 generation service for role-tailored cover letters and tailored resumes."
        ]),
        ("Sprint 4: AI Voice Interview Simulator, UI Polish & Cloud Deployment", "Weeks 7–8", "Complete interview simulator, conversational copilot, dual theme UI, and cloud release.", [
            "Integrate Web Speech API for voice dictation in interview practice questions.",
            "Develop multi-criteria interview scoring engine (relevance, technical depth, STAR structure).",
            "Build 24/7 conversational career assistant with persistent chat history.",
            "Deploy to Render cloud platform, automate keep-alive monitoring, and finalize documentation."
        ])
    ]

    for title, dur, goal, tasks in sprint_plans:
        add_heading_styled(doc, title, 2, space_before=10, space_after=4)
        add_body_p(doc, f"{dur}  |  Goal: {goal}", bold_prefix="Timeline & Goal: ")
        for t in tasks:
            add_body_p(doc, t, bullet=True)

    # --------------------------------------------------------------------------
    # SECTION 8: SPRINT TASKS & STATUS
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "8. Sprint Tasks & Status", 1)
    add_body_p(doc, "Tracking of sprint task execution across the internship development cycles:")

    sprint_tasks_headers = ["Sprint", "Task Description", "Assigned To", "Status"]
    sprint_tasks_data = [
        ["Sprint 1", "FastAPI architecture & environment setup", "Arun", "Done"],
        ["Sprint 1", "SQLAlchemy database schemas & migrations", "Arun", "Done"],
        ["Sprint 1", "JWT authentication & password hashing", "Arun", "Done"],
        ["Sprint 1", "Candidate Talent Profile UI & state", "Arun", "Done"],
        ["Sprint 2", "PDF/DOCX file upload & parsing engine", "Arun", "Done"],
        ["Sprint 2", "Skill extraction & ATS score computation", "Arun", "Done"],
        ["Sprint 2", "ChromaDB vector database integration", "Arun", "Done"],
        ["Sprint 2", "Seed 22 multi-department internships", "Arun", "Done"],
        ["Sprint 3", "Hybrid compatibility scoring algorithm", "Arun", "Done"],
        ["Sprint 3", "Skill gap diagnostic & roadmaps", "Arun", "Done"],
        ["Sprint 3", "Targeted cover letter & resume generator", "Arun", "Done"],
        ["Sprint 4", "Voice-enabled AI mock interview simulator", "Arun", "Done"],
        ["Sprint 4", "24/7 Conversational career copilot", "Arun", "Done"],
        ["Sprint 4", "Dual Light/Dark theme design system", "Arun", "Done"],
        ["Sprint 4", "Render cloud deployment & keep-alive cron", "Arun", "Done"]
    ]
    sprint_tbl = doc.add_table(rows=1, cols=4)
    format_table(sprint_tbl, [1.0, 3.27, 1.2, 0.8], sprint_tasks_headers, sprint_tasks_data, header_bg="1E3A8A")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 9: IMPLEMENTATION & KEY FEATURES (THE 8 MODULES)
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "9. Implementation / Key Features", 1)
    add_body_p(doc, "The platform is structured into eight production modules, each solving a distinct aspect of the career preparation lifecycle:")

    modules_data = [
        ("Module 1: Student Academic & Career Profile (/profile)",
         "Central repository of the candidate's verified identity, talent DNA, contact details, academic background, GPA, technical skills inventory, and preferred career tracks.",
         "Implemented using FastAPI `/api/profile` endpoints backed by SQLite ORM. Includes full CRUD operations and safeguards candidate identity during resume uploads.",
         "Endpoint: GET/PUT `/api/profile/me` | Output: Structured JSON talent profile and interactive UI cards."),

        ("Module 2: Resume Parsing & ATS Skill Extraction (/resume-parser)",
         "Automated ingestion of PDF/DOCX resumes, extracting contact information, detected technical and soft skills, work experience, education, and ATS readiness scores.",
         "Employs `pypdf` and `docx2txt` with regex and pattern matching. Features an ATS scoring rubric evaluating length, action verbs, quantified results, and skill density.",
         "Endpoint: POST `/resumes/upload` | Output: Extracted JSON talent graph, ATS score (0-100%), and 1-click sample demo profile."),

        ("Module 3: Internship Knowledge Base with RAG Retrieval (/knowledge-base)",
         "Curated database of 22 active multi-department internships (AI, Data Science, Full-Stack, Cloud, DevOps) queryable via semantic natural language search.",
         "Indexed in ChromaDB using `all-MiniLM-L6-v2` dense vector embeddings. Natural language user queries perform top-k cosine similarity retrieval with metadata filtering.",
         "Endpoint: GET `/internships` & POST `/internships/search` | Output: Ranked internship cards with stipend, duration, and requirements."),

        ("Module 4: Job-Resume Compatibility & Match Scoring (/job-matching)",
         "Objective mathematical matching between parsed candidate resume profiles and internship listings.",
         "Combines TF-IDF keyword overlap (40% weight) with dense vector cosine similarity (60% weight). Displays overall match percentage, matched skills, and missing competencies.",
         "Endpoint: POST `/matching/score` | Output: Match score breakdown (e.g., 88% Strong Match) with visual match badges."),

        ("Module 5: Skill Gap Analysis & Improvement Recommendations (/skill-gap)",
         "Diagnostic assessment identifying skill deficiencies against target roles and generating step-by-step upskilling roadmaps.",
         "Compares candidate skill vectors with job prerequisites, separating gaps into Critical Gaps, Secondary Deficits, and Recommended Certifications with direct course links.",
         "Endpoint: POST `/matching/skill-gap` | Output: Actionable learning roadmap with estimated time-to-competency."),

        ("Module 6: Role-Specific Resume & Cover Letter Customization (/cover-letter)",
         "AI-powered generation of tailored cover letters and customized resume bullet points aligned to specific job descriptions.",
         "Prompts Groq LLaMA 3.3 70B with candidate credentials and job requirements, enforcing formal business letter etiquette and highlighting relevant achievements.",
         "Endpoint: POST `/cv/generate-cover-letter` | Output: Ready-to-send personalized cover letter and tailored resume copy."),

        ("Module 7: AI Interview Preparation & Voice Simulation (/interview-prep)",
         "Simulates role-specific technical, behavioral, and situational mock interviews with real-time speech-to-text dictation and objective STAR scoring.",
         "Generates targeted interview questions based on role. Captures audio via Web Speech API, analyzes candidate answers, and scores on Technical Depth, Relevance, and Structure.",
         "Endpoint: POST `/interview/generate` & `/interview/evaluate` | Output: Instant interview scorecards and improvement tips."),

        ("Module 8: Conversational Career Assistant (/career-assistant)",
         "24/7 intelligent career co-pilot providing continuous guidance, resume advice, market salary insights, and placement preparation.",
         "FastAPI chat endpoint integrated with Groq LLaMA 3.3 70B with full conversation history and domain-constrained system prompts.",
         "Endpoint: POST `/agent/chat` | Output: Real-time contextual career responses and guided next-action recommendations.")
    ]

    for m_title, desc, impl, out in modules_data:
        add_heading_styled(doc, m_title, 2, space_before=8, space_after=2)
        add_body_p(doc, desc, bold_prefix="Description: ")
        add_body_p(doc, impl, bold_prefix="Implementation: ")
        add_body_p(doc, out, bold_prefix="Deliverable: ", space_after=6)

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 10: TESTING
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "10. Testing", 1)
    add_body_p(doc, "Rigorous multi-layer testing was conducted across all microservices, API routes, and user interface components to verify functional correctness:")

    test_headers = ["Test ID", "Test Case Description", "Expected Result", "Actual Result", "Status"]
    test_data = [
        ["T001", "User registration with unique email", "User created with hashed password & JWT issued", "User created; 201 Created returned", "Pass"],
        ["T002", "Login with valid credentials", "JWT access token returned and saved", "Token received and stored in localStorage", "Pass"],
        ["T003", "Login with invalid password", "HTTP 401 Unauthorized with error message", "HTTP 401 returned; error toast shown", "Pass"],
        ["T004", "Upload standard PDF resume", "Text extracted, skills identified, ATS score computed", "Skills extracted into talent profile (85% ATS)", "Pass"],
        ["T005", "1-Click Seed Demo Resume", "Sample profile populated without file upload", "Demo candidate profile loaded instantly", "Pass"],
        ["T006", "Semantic search on Knowledge Base", "Return top-k relevant internships via vector similarity", "Top 5 matching internships returned in < 200ms", "Pass"],
        ["T007", "Job-Resume Compatibility Scoring", "Compute hybrid TF-IDF + Cosine match percentage", "Accurate match percentage (e.g. 84%) rendered", "Pass"],
        ["T008", "Skill Gap Diagnostic Roadmap", "Identify missing skills and recommend learning path", "Critical & secondary gaps identified with courses", "Pass"],
        ["T009", "Mock Interview Voice Dictation", "Web Speech API transcribes candidate spoken response", "Spoken audio transcribed accurately into text field", "Pass"],
        ["T010", "Keep-Alive Health Ping", "GET /health returns HTTP 200 with healthy status", "HTTP 200 OK returned; keeps server active 24/7", "Pass"]
    ]
    test_tbl = doc.add_table(rows=1, cols=5)
    format_table(test_tbl, [0.6, 2.0, 1.87, 1.3, 0.5], test_headers, test_data, header_bg="1E3A8A")

    add_heading_styled(doc, "10.1 Testing Types Performed", 2, space_before=10)
    add_body_p(doc, "Verified all 8 module endpoints using FastAPI TestClient and Swagger UI.", bullet=True, bold_prefix="API Integration Testing: ")
    add_body_p(doc, "Validated user flows from login to resume upload, matching, and interview evaluation.", bullet=True, bold_prefix="End-to-End Functional Testing: ")
    add_body_p(doc, "Verified responsive design across mobile, tablet, and desktop screens in both Light and Dark themes.", bullet=True, bold_prefix="UI & Cross-Device Testing: ")
    add_body_p(doc, "Measured Groq LPU inference latency (< 1.5s) and ChromaDB retrieval latency (< 250ms).", bullet=True, bold_prefix="Performance Testing: ")

    # --------------------------------------------------------------------------
    # SECTION 11: CHALLENGES & ENGINEERING SOLUTIONS
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "11. Challenges & Solutions", 1)
    add_body_p(doc, "Key engineering challenges encountered during development and how they were systematically resolved:")

    challenges_headers = ["Engineering Challenge Faced", "Root Cause Analysis", "Applied Technical Solution"]
    challenges_data = [
        ["PDF Text Extraction Anomaly",
         "Varied multi-column resume layouts caused fragmented text ordering and missed skill keywords.",
         "Implemented a dual extraction pipeline combining PyPDF text extraction with regex normalization and fallback character cleaning."],
        ["Semantic vs Keyword Mismatch",
         "Pure keyword matching missed semantically identical skills (e.g., 'ML' vs 'Machine Learning'); pure vector search missed exact syntax.",
         "Engineered a hybrid compatibility scoring formula blending TF-IDF keyword overlap (40%) and dense sentence-transformer cosine similarity (60%)."],
        ["Render Cloud Import Path Error",
         "Render's execution environment launched Uvicorn from the repository root, failing to locate `app` module inside `backend/`.",
         "Created a top-level `main.py` entry point that explicitly prepends the backend directory to `sys.path` prior to starting Uvicorn."],
        ["Cloud Free-Tier Inactivity Sleep",
         "Render free instances spin down after 15 minutes of inactivity, causing a 50-second wake-up screen for initial visitors.",
         "Configured an automated keep-alive cron job via Cron-Job.org pinging the `/health` endpoint every 10 minutes, keeping the instance active 24/7."],
        ["Default Dark Theme Launch",
         "System-level `prefers-color-scheme: dark` media query triggered automatic dark mode on initial load for users with dark OS settings.",
         "Updated ThemeContext to default strictly to Light Theme for all new sessions while preserving user toggle preferences in localStorage."]
    ]
    chal_tbl = doc.add_table(rows=1, cols=3)
    format_table(chal_tbl, [1.8, 2.2, 2.27], challenges_headers, challenges_data, header_bg="1E3A8A")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # SECTION 12: FINAL PROJECT STATUS
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "12. Final Project Status", 1)
    add_body_p(doc, "The AI Career Companion platform has been 100% developed, thoroughly tested, and successfully deployed to live cloud infrastructure.")

    add_heading_styled(doc, "12.1 Completed Modules Checklist", 2)
    add_body_p(doc, "Module 1: Student Academic & Career Profile (Talent DNA)", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 2: Resume Parsing & ATS Intelligence Extraction", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 3: Internship Knowledge Base & ChromaDB RAG Retrieval", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 4: Job-Resume Compatibility & Hybrid Match Scoring", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 5: Skill Gap Diagnostics & Upskilling Roadmaps", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 6: Role-Specific Resume & Cover Letter Tailoring", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 7: AI Voice/Text Mock Interview Preparation Simulator", bullet=True, bold_prefix="[100% Complete] ")
    add_body_p(doc, "Module 8: 24/7 Conversational Career Assistant Copilot", bullet=True, bold_prefix="[100% Complete] ")

    add_heading_styled(doc, "12.2 Production Links & Access Deliverables", 2)
    add_body_p(doc, "https://ai-career-companion-mg65.onrender.com", bold_prefix="Live Web Application: ")
    add_body_p(doc, "https://ai-career-companion-mg65.onrender.com/docs", bold_prefix="Interactive Swagger API Docs: ")
    add_body_p(doc, "https://github.com/U-ARUN07/ai-career-companion", bold_prefix="GitHub Source Repository: ")
    add_body_p(doc, "arun.student@example.com  |  Password: Student123! (1-Click button available on login page)", bold_prefix="Demo Student Credentials: ")

    add_heading_styled(doc, "12.3 Final Outcome & Impact", 2)
    add_body_p(doc, "The completed platform successfully solves the core challenges of modern internship recruitment. By combining deterministic vector embeddings, high-speed LLM reasoning via Groq Cloud, and a modern responsive interface, students can evaluate their placement readiness, bridge technical skill gaps, and practice role-specific interviews with confidence. The platform stands fully operational and ready for official academic and corporate evaluation.")

    doc.add_page_break()

    # --------------------------------------------------------------------------
    # APPENDIX: 10-SLIDE PROJECT PPT STRUCTURE
    # --------------------------------------------------------------------------
    add_heading_styled(doc, "Appendix: 10-Slide Project Presentation Script", 1)
    add_body_p(doc, "This slide deck structure is designed for the final project presentation with mentor Mr. Vijay Parmar:")

    slides_data = [
        ("Slide 1: Title & Introduction",
         "Project Name: AI Career Companion | Subtitle: Unified RAG Career Intelligence Platform\nCandidate: Arun | Mentor: Vijay Parmar | Program: Infosys Springboard VIP 7.0"),
        ("Slide 2: Problem Statement",
         "The Broken Internship Pipeline: Fragmented job boards, 75%+ ATS resume rejection rate, zero actionable feedback on missing skills, and generic, unhelpful interview preparation."),
        ("Slide 3: Project Objective & Vision",
         "Deliver a unified AI ecosystem that ingests resumes, matches candidates to internships using RAG semantic search, diagnoses skill deficits, generates tailored applications, and conducts mock interviews."),
        ("Slide 4: Proposed Solution & System Flow",
         "Interactive Architecture: User -> React 19 Frontend -> FastAPI Backend -> ChromaDB Vector Store -> Groq LLaMA 3.3 70B -> Instant Personalized Career Intelligence."),
        ("Slide 5: Technology Stack",
         "Frontend: React 19, Vite, Lucide Icons | Backend: FastAPI, Python 3.14, SQLAlchemy | AI/RAG: ChromaDB, Sentence-Transformers, Groq LPU | Cloud: Render, Git, Cron-Job.org."),
        ("Slide 6: Key Features & 8 Core Modules",
         "1. Profile DNA | 2. Resume Parser | 3. RAG Knowledge Base | 4. Compatibility Scoring | 5. Skill Gap Roadmaps | 6. Tailored Cover Letters | 7. Mock Interview Simulator | 8. 24/7 Career Copilot."),
        ("Slide 7: Agile Methodology & Sprints",
         "Product Backlog & 4 Sprints: Sprint 1 (Auth & Architecture) -> Sprint 2 (Parser & ChromaDB) -> Sprint 3 (Matching & Skill Gap) -> Sprint 4 (Interview Simulator, UI & Cloud Deployment)."),
        ("Slide 8: System Architecture & RAG Pipeline",
         "Deep-dive into vector embeddings: Document Chunking -> 384-d dense embeddings -> ChromaDB cosine index -> Hybrid TF-IDF + Cosine scoring -> Low-latency (<1.5s) LLM response generation."),
        ("Slide 9: Testing, Verification & Results",
         "10 Comprehensive Test Cases: 100% Pass Rate across Auth, Parser, Matching, Interview Voice Dictation, and Keep-Alive Monitoring. Live cloud uptime verified 24/7 on Render."),
        ("Slide 10: Conclusion & Future Scope",
         "Conclusion: Successfully delivered production platform fulfilling all VIP 7.0 requirements.\nFuture Scope: Integration with LinkedIn API, automated multi-agent coding challenge evaluator, and campus placement portal integration.")
    ]

    for s_title, s_content in slides_data:
        add_heading_styled(doc, s_title, 2, space_before=8, space_after=2)
        add_body_p(doc, s_content, space_after=6)

    doc.save("Agile Documentation.docx")
    print("Agile Documentation.docx successfully generated!")

if __name__ == "__main__":
    build_full_documentation()
