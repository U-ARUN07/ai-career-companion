import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api from "../services/api";
import BrandLogo from "../components/BrandLogo";
import { useTheme } from "../context/ThemeContext";

export function LandingPage() {
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const heroRotatingPhrases = [
    "Deep ATS Resume Parsing",
    "Precision Job Matching",
    "Skill Gap Roadmaps",
    "Role-Specific CV Architect",
    "AI Mock Interview Coaching",
    "Autonomous Career Mentorship"
  ];

  const [phraseIndex, setPhraseIndex] = useState(0);
  const [fadeState, setFadeState] = useState("fade-in");

  useEffect(() => {
    const timer = setInterval(() => {
      setFadeState("fade-out");
      setTimeout(() => {
        setPhraseIndex((prev) => (prev + 1) % heroRotatingPhrases.length);
        setFadeState("fade-in");
      }, 350);
    }, 3200);
    return () => clearInterval(timer);
  }, []);

  const modules = [
    {
      id: 1,
      title: "1. Profile & Resume Mgmt",
      desc: "Maintain your student academic profile and manage active resume versions seamlessly.",
      icon: "👤",
      path: "/profile"
    },
    {
      id: 2,
      title: "2. Deep Resume Parsing",
      desc: "Extract technical and soft skills, projects, and work history with AI verification.",
      icon: "📄",
      path: "/resume-parser"
    },
    {
      id: 3,
      title: "3. Internship Opportunities",
      desc: "Explore verified internship openings across leading tech companies with AI-assisted querying.",
      icon: "💼",
      path: "/knowledge-base"
    },
    {
      id: 4,
      title: "4. Job-Resume Matching",
      desc: "Multi-factor compatibility scoring comparing skills, experience, and domain fit.",
      icon: "🎯",
      path: "/job-matching"
    },
    {
      id: 5,
      title: "5. Skill Gap Analysis",
      desc: "Identify missing skills with customized learning roadmaps, courses, and project ideas.",
      icon: "📈",
      path: "/skill-gap"
    },
    {
      id: 6,
      title: "6. Resume & Cover Letter",
      desc: "AI tailor your resume bullets and generate company-specific cover letters.",
      icon: "✍️",
      path: "/customizer"
    },
    {
      id: 7,
      title: "7. Interview Preparation",
      desc: "Role-specific technical and STAR behavioral questions with AI answer grading.",
      icon: "🎙️",
      path: "/interview-prep"
    },
    {
      id: 8,
      title: "8. Ask AI Mentor",
      desc: "Continuous conversational AI mentorship loaded with your personal profile, resume, and skills context.",
      icon: "💬",
      path: "/career-assistant"
    }
  ];

  const candName = "Arun";
  const candRole = localStorage.getItem("target_role") || "Full-Stack AI Engineer Intern";
  const isChemical = candRole.toLowerCase().includes("chemical") || candRole.toLowerCase().includes("process");

  useEffect(() => {
    // Ensure legacy cached names are normalized to Arun
    const stored = localStorage.getItem("user_name");
    if (!stored || stored.toLowerCase().includes("aruna") || stored.toLowerCase().includes("katravath") || stored.toLowerCase().includes("rakesh")) {
      localStorage.setItem("user_name", "Arun");
    }
  }, []);

  const handleModuleClick = (path) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate(path);
    } else {
      navigate(`/login?redirect=${encodeURIComponent(path)}`);
    }
  };

  return (
    <div className="landing-page" id="top">
      {/* 1. FLOATING COMMAND DOCK */}
      <header className="landing-command-dock-wrap">
        <nav className="landing-command-dock">
          <a
            href="#top"
            className="dock-logo-anchor"
            onClick={(e) => {
              e.preventDefault();
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            title="AI Career Companion - Back to Top"
          >
            <BrandLogo size="sm" showBadge={false} />
            <span className="dock-live-pulse-badge">
              <span className="dock-ping-dot"></span>
              <span>v2.0 Autonomous</span>
            </span>
          </a>

          <div className="dock-nav-pills">
            <a href="#stage" className="dock-pill-link">Autonomous Stage</a>
            <a href="#bento" className="dock-pill-link">Intelligence Bento</a>
            <a href="#pipeline" className="dock-pill-link">Architecture Flow</a>
            <a href="#telemetry" className="dock-pill-link">Live Metrics</a>
          </div>

          <div className="dock-actions-row">
            <button
              type="button"
              onClick={toggleTheme}
              className="dock-theme-btn"
              title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
              aria-label="Toggle Theme"
            >
              <span>{theme === "dark" ? "☀️" : "🌙"}</span>
            </button>
            <Link to="/login" className="dock-login-btn">
              Sign In
            </Link>
            <Link to="/register" className="dock-cta-btn">
              <span>Launch Cockpit</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </Link>
          </div>
        </nav>
      </header>

      {/* 2. GRAND STAGE EXECUTIVE HERO */}
      <section className="executive-stage-hero" id="stage">
        <div className="stage-hero-inner">
          <div className="stage-eyebrow-chip">
            <span className="chip-bolt">⚡</span>
            <span>AUTONOMOUS CAREER ACCELERATION ENGINE • INFOSYS VIP 7.0</span>
          </div>

          <h1 className="stage-hero-headline">
            <span className="stage-line1">Accelerate Your Career with</span>
            <div className="stage-rotating-capsule">
              <span className={`stage-changing-text ${fadeState}`}>
                {heroRotatingPhrases[phraseIndex]}
              </span>
            </div>
          </h1>

          <p className="stage-hero-lead">
            An end-to-end autonomous AI career intelligence system uniting 
            <strong> Deep ATS Extraction</strong>, <strong> 384-Dim Vector RAG Matching</strong>, 
            <strong> Dynamic Skill Gap Roadmaps</strong>, <strong> Executive CV Architect</strong>, and 
            <strong> Real-Time Voice Mock Simulations</strong>.
          </p>

          <div className="stage-cta-deck">
            <Link to="/register" className="stage-btn-primary">
              <span>⚡ Enter Career Cockpit</span>
            </Link>
            <a href="#bento" className="stage-btn-secondary">
              <span>Explore 8 Intelligence Suites ↓</span>
            </a>
          </div>
        </div>

        {/* 3. PANORAMIC LIVE TELEMETRY CONSOLE (FULL-WIDTH 3-BAY VIEW) */}
        <div className="panoramic-console-wrap">
          <div className="panoramic-console">
            {/* Top Console Bezel */}
            <div className="console-bezel-top">
              <div className="console-traffic-lights">
                <span className="c-dot c-red"></span>
                <span className="c-dot c-yellow"></span>
                <span className="c-dot c-green"></span>
              </div>
              <div className="console-title-chip">
                <span className="console-ping"></span>
                <span>GROQ CLOUD LLaMA-3.3 70B • LATENCY &lt; 180ms • CANDIDATE: {candName.toUpperCase()}</span>
              </div>
              <div className="console-pill-active">
                <span>94% READINESS</span>
              </div>
            </div>

            {/* 3 Synchronized Live Bays */}
            <div className="console-bays-grid">
              {/* Bay 1: Candidate Talent DNA */}
              <div className="console-bay bay-talent">
                <div className="bay-badge-row">
                  <span className="bay-label">BAY 01 • TALENT DNA</span>
                  <span className="bay-status">VERIFIED</span>
                </div>
                <div className="bay-candidate-card">
                  <div className="b-avatar">{candName.charAt(0).toUpperCase()}</div>
                  <div className="b-meta">
                    <strong>{candName}</strong>
                    <span>Target: {candRole}</span>
                    <small>Hyderabad / Bengaluru (Open to Remote)</small>
                  </div>
                  <div className="b-score-circle">
                    <strong>96%</strong>
                    <small>FIT</small>
                  </div>
                </div>
                <div className="bay-skills-cloud">
                  {isChemical ? (
                    <>
                      <span className="b-chip chip-hit">✓ Heat Transfer</span>
                      <span className="b-chip chip-hit">✓ Mass Transfer</span>
                      <span className="b-chip chip-hit">✓ Fluid Mechanics</span>
                      <span className="b-chip chip-hit">✓ C / Matlab</span>
                      <span className="b-chip chip-hit">✓ Process Safety</span>
                      <span className="b-chip chip-gap">+ DCS Controls</span>
                    </>
                  ) : (
                    <>
                      <span className="b-chip chip-hit">✓ Python & FastAPI</span>
                      <span className="b-chip chip-hit">✓ 384-Dim RAG (FAISS)</span>
                      <span className="b-chip chip-hit">✓ React 18 UI</span>
                      <span className="b-chip chip-hit">✓ Docker & PostgreSQL</span>
                      <span className="b-chip chip-hit">✓ System Design</span>
                      <span className="b-chip chip-gap">+ Kubernetes</span>
                    </>
                  )}
                </div>
              </div>

              {/* Bay 2: Live Semantic Vector Search Radar */}
              <div className="console-bay bay-matching">
                <div className="bay-badge-row">
                  <span className="bay-label">BAY 02 • 384-DIM RAG RADAR</span>
                  <span className="bay-status">COSINE: 0.962</span>
                </div>
                <div className="bay-job-spotlight">
                  <div className="b-job-head">
                    <div>
                      <h5>{isChemical ? "Chemical Process & Plant Operations Trainee" : "Full-Stack AI & Software Engineer Intern"}</h5>
                      <span className="b-company">{isChemical ? "Reliance Petrochem & RFCL Solutions" : "TechCorp Innovations"} • Hybrid</span>
                    </div>
                    <span className="b-stipend">₹35,000 / mo</span>
                  </div>
                  <div className="b-vector-stats">
                    <div className="stat-col">
                      <span className="sc-lbl">Skill Match</span>
                      <strong className="sc-val">96%</strong>
                    </div>
                    <div className="stat-col">
                      <span className="sc-lbl">Domain Fit</span>
                      <strong className="sc-val">98%</strong>
                    </div>
                    <div className="stat-col">
                      <span className="sc-lbl">Experience</span>
                      <strong className="sc-val">92%</strong>
                    </div>
                  </div>
                </div>
                <button type="button" onClick={() => handleModuleClick("/job-matching")} className="bay-action-pill">
                  Run Multi-Vector Audit →
                </button>
              </div>

              {/* Bay 3: Autonomous Career Copilot Stream */}
              <div className="console-bay bay-copilot">
                <div className="bay-badge-row">
                  <span className="bay-label">BAY 03 • AUTONOMOUS COPILOT</span>
                  <span className="bay-status">LLaMA 3.3 READY</span>
                </div>
                <div className="bay-chat-stream">
                  <div className="chat-bubble bubble-ai">
                    <span className="ai-icon">⚡</span>
                    <div className="ai-msg">
                      <strong>AI Career Mentor:</strong>
                      <p>"{candName}, your verified skills and industrial milestones align 96% with target recruiter hiring rubrics. Practice our STAR behavioral mock next!"</p>
                    </div>
                  </div>
                  <div className="bay-mock-feedback">
                    <span className="feedback-score">★ 9.4 / 10 Mock Score</span>
                    <span>"Clear architectural trade-offs demonstrated"</span>
                  </div>
                </div>
                <button type="button" onClick={() => handleModuleClick("/career-assistant")} className="bay-action-pill">
                  Open AI Mentor Desk →
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. HIGH-TECH METRICS TELEMETRY RIBBON */}
      <section className="telemetry-ribbon" id="telemetry">
        <div className="ribbon-inner">
          <div className="metric-cell">
            <strong className="metric-val">&lt; 0.20s</strong>
            <span className="metric-desc">Groq LLaMA Inference Speed</span>
          </div>
          <div className="metric-divider"></div>
          <div className="metric-cell">
            <strong className="metric-val">384-Dim</strong>
            <span className="metric-desc">Dense Vector FAISS Embeddings</span>
          </div>
          <div className="metric-divider"></div>
          <div className="metric-cell">
            <strong className="metric-val">94%</strong>
            <span className="metric-desc">Student Placement Readiness</span>
          </div>
          <div className="metric-divider"></div>
          <div className="metric-cell">
            <strong className="metric-val">8 of 8</strong>
            <span className="metric-desc">Autonomous Intelligence Modules</span>
          </div>
        </div>
      </section>

      {/* 5. THE ENTERPRISE INTELLIGENCE MATRIX (ALL 8 MODULES) */}
      <section className="bento-matrix-section" id="bento">
        <div className="bento-section-header">
          <div className="bento-badge">ENTERPRISE INTELLIGENCE MATRIX</div>
          <h2>8 Fully Autonomous Operational Suites</h2>
          <p>Engineered for ambitious candidates across all disciplines — Engineering, Technology, Marketing, Finance, HR, Design & Operations.</p>
        </div>

        <div className="bento-grid-container">
          {/* Card 1: Module 01 - Candidate Profile */}
          <div className="bento-card bento-profile" onClick={() => handleModuleClick("/profile")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 01</span>
              <span className="bento-status-pill">CENTRAL TALENT DNA</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <h3>Candidate Profile & Credentials</h3>
              <p>Unify candidate contact info, academic credentials, verified skills, and career target roles across any academic discipline.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Academic History</span>
                <span className="prev-pill">✓ Verified Skills</span>
                <span className="prev-pill">✓ Master Profile Sync</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Manage Candidate Profile →</span>
            </div>
          </div>

          {/* Card 2: Module 02 - Resume Parser */}
          <div className="bento-card bento-parser" onClick={() => handleModuleClick("/resume-parser")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 02</span>
              <span className="bento-status-pill">SECTION-AWARE EXTRACTION</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
              </div>
              <h3>Deep ATS Resume Parser & Structural Audit</h3>
              <p>Extract verified domain skills, software tools, leadership competencies, and quantitative impact bullets with automatic ATS scoring.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Verified Entities</span>
                <span className="prev-pill">✓ Real Experience</span>
                <span className="prev-pill">✓ 100% ATS Formatted</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Launch ATS Audit Studio →</span>
            </div>
          </div>

          {/* Card 3: Module 03 - Internship Radar */}
          <div className="bento-card bento-radar" onClick={() => handleModuleClick("/knowledge-base")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 03</span>
              <span className="bento-status-pill">LIVE MARKET RADAR</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
              </div>
              <h3>Curated Internship Opportunities Radar</h3>
              <p>Explore verified opportunities across Chemical, Mechanical, Civil, IT, Finance, Marketing, and People Operations with live stipends.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Multi-Domain</span>
                <span className="prev-pill">✓ Verified Stipends</span>
                <span className="prev-pill">✓ 1-Click Filters</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Explore Internship Radar →</span>
            </div>
          </div>

          {/* Card 4: Module 04 - Semantic RAG Matching */}
          <div className="bento-card bento-matching" onClick={() => handleModuleClick("/job-matching")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 04</span>
              <span className="bento-status-pill">FAISS DENSE COSINE MATCH</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              </div>
              <h3>Semantic RAG Matching & Compatibility</h3>
              <p>Compare candidate vector embeddings against multi-discipline opportunities with domain-weighted precision and explainable scores.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Reliance / RFCL: 95%</span>
                <span className="prev-pill">✓ TechCorp: 94%</span>
                <span className="prev-pill">✓ Apex Capital: 91%</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Run Compatibility Match →</span>
            </div>
          </div>

          {/* Card 5: Module 05 - Skill Gap */}
          <div className="bento-card bento-skillgap" onClick={() => handleModuleClick("/skill-gap")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 05</span>
              <span className="bento-status-pill">ROADMAP ENGINE</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
              </div>
              <h3>Skill Gap Diagnostics & Sprints</h3>
              <p>Identify missing recruiter hiring filters and generate structured 4-week learning sprints with verified open-source resources.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Missing Filters</span>
                <span className="prev-pill">✓ 4-Week Sprints</span>
                <span className="prev-pill">✓ Curated Links</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">View Learning Roadmap →</span>
            </div>
          </div>

          {/* Card 6: Module 06 - CV Architect */}
          <div className="bento-card bento-cv" onClick={() => handleModuleClick("/customizer")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 06</span>
              <span className="bento-status-pill">EXECUTIVE PDF ARCHITECT</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              </div>
              <h3>Role-Specific CV & Cover Letter Architect</h3>
              <p>Generate high-contrast, executive PDF resumes and tailored cover letters hydrated directly from your verified extraction.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ 3 Modern Templates</span>
                <span className="prev-pill">✓ Dynamic Data</span>
                <span className="prev-pill">✓ Instant PDF</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Generate Official PDF CV →</span>
            </div>
          </div>

          {/* Card 7: Module 07 - Interview Simulator */}
          <div className="bento-card bento-interview" onClick={() => handleModuleClick("/interview-prep")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 07</span>
              <span className="bento-status-pill">AI VOICE & STAR RUBRIC</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
              </div>
              <h3>Technical & Behavioral Mock Simulator</h3>
              <p>Practice role-targeted challenges across your discipline and receive instant STAR-method evaluation rubrics.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ Voice Synthesis</span>
                <span className="prev-pill">✓ STAR Scoring</span>
                <span className="prev-pill">✓ Custom Rubrics</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Start Mock Practice →</span>
            </div>
          </div>

          {/* Card 8: Module 08 - AI Career Copilot */}
          <div className="bento-card bento-copilot" onClick={() => handleModuleClick("/career-assistant")} role="button" tabIndex={0}>
            <div className="bento-card-top">
              <span className="bento-mod-tag">MODULE 08</span>
              <span className="bento-status-pill">RAG CAREER AGENT</span>
            </div>
            <div className="bento-card-body">
              <div className="bento-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>
              </div>
              <h3>Conversational AI Career Copilot</h3>
              <p>Continuous career mentorship grounded in your verified academic and resume profile data with real-time domain advice.</p>
              <div className="bento-mini-preview">
                <span className="prev-pill">✓ RAG Grounded</span>
                <span className="prev-pill">✓ Domain Mentorship</span>
                <span className="prev-pill">✓ 24/7 Co-Pilot</span>
              </div>
            </div>
            <div className="bento-card-footer">
              <span className="bento-link">Ask AI Mentor Desk →</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. ENTERPRISE SYSTEM FLOW ARCHITECTURE */}
      <section className="system-flow-section" id="pipeline">
        <div className="flow-inner">
          <div className="flow-header">
            <span className="flow-badge">FULL-STACK DATA TELEMETRY</span>
            <h3>End-to-End Autonomous Progression Pipeline</h3>
            <p>From unparsed resume documents to verified enterprise internship placement across all industry domains</p>
          </div>

          <div className="flow-steps-chain">
            <div className="flow-node">
              <span className="node-num">01</span>
              <strong>Document Ingestion</strong>
              <p>PyMuPDF parses PDF / DOCX into structured text tokens</p>
            </div>
            <div className="flow-arrow">➔</div>
            <div className="flow-node">
              <span className="node-num">02</span>
              <strong>AI Entity Extraction</strong>
              <p>Section-aware engine extracts verified skills, projects & experience</p>
            </div>
            <div className="flow-arrow">➔</div>
            <div className="flow-node">
              <span className="node-num">03</span>
              <strong>384-Dim FAISS Index</strong>
              <p>Semantic vector dense search matches multi-domain opportunities</p>
            </div>
            <div className="flow-arrow">➔</div>
            <div className="flow-node">
              <span className="node-num">04</span>
              <strong>Mock & Roadmap Prep</strong>
              <p>STAR behavioral simulator prepares candidate for offers</p>
            </div>
            <div className="flow-arrow">➔</div>
            <div className="flow-node flow-node-target">
              <span className="node-num">05</span>
              <strong>Placement Ready 🎯</strong>
              <p>94% verified candidate placement readiness index</p>
            </div>
          </div>
        </div>
      </section>

      {/* Comprehensive Landing Page Footer */}
      <footer className="landing-footer-modern">
        <div className="footer-top-grid">
          {/* Col 1: Brand & Mission */}
          <div className="footer-col footer-col-brand">
            <BrandLogo size="md" showBadge={false} inverted={true} />
            <p className="footer-brand-mission">
              Empowering the next generation of students and professionals across all disciplines with an integrated, autonomous career accelerator: semantic RAG job matching, real-time resume ATS optimization, mock interviews, and personalized AI career mentorship.
            </p>
            <div className="footer-status-pill">
              <span className="status-indicator-dot"></span>
              <span>All 8 Intelligence Modules Live</span>
            </div>
          </div>

          {/* Col 2: Intelligence Suite */}
          <div className="footer-col">
            <h4>Intelligence Suite</h4>
            <ul>
              <li><button type="button" onClick={() => handleModuleClick("/profile")} className="footer-nav-btn">1. Student Profile & Resumes</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/resume-parser")} className="footer-nav-btn">2. Deep Resume Parser</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/knowledge-base")} className="footer-nav-btn">3. Internship Opportunities</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/job-matching")} className="footer-nav-btn">4. Compatibility Scoring</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/skill-gap")} className="footer-nav-btn">5. Skill Gap Analysis</button></li>
            </ul>
          </div>

          {/* Col 3: Career Tools */}
          <div className="footer-col">
            <h4>Career Acceleration</h4>
            <ul>
              <li><button type="button" onClick={() => handleModuleClick("/customizer")} className="footer-nav-btn">6. Role-Specific ATS CV</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/interview-prep")} className="footer-nav-btn">7. Mock Interview Practice</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/career-assistant")} className="footer-nav-btn">8. Conversational AI Mentor</button></li>
              <li><button type="button" onClick={() => handleModuleClick("/customizer")} className="footer-nav-btn">📄 1-Click PDF CV Exporter</button></li>
            </ul>
          </div>

          {/* Col 4: Platform & Access */}
          <div className="footer-col">
            <h4>Platform & Access</h4>
            <ul>
              <li><a href="http://127.0.0.1:8001/docs" target="_blank" rel="noreferrer">FastAPI REST Docs ↗</a></li>
              <li><Link to="/login">Student Portal Sign In</Link></li>
              <li><Link to="/register">Create Free Account</Link></li>
              <li><a href="#modules">System Architecture</a></li>
              <li><Link to="/login?redirect=%2Fcareer-assistant">Contact AI Mentor Desk</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom Legal Bar */}
        <div className="footer-bottom-bar">
          <p>© 2026 AI Career Companion Platform. Built for ambitious students seeking top internships across all industry domains.</p>
          <div className="footer-bottom-links">
            <span className="footer-mini-link">Terms of Service</span>
            <span className="dot-sep">•</span>
            <span className="footer-mini-link">Privacy Policy</span>
            <span className="dot-sep">•</span>
            <span className="footer-mini-link">Academic License</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  // Always land at Dashboard on login as explicitly requested by user
  const redirectPath = "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const { theme, toggleTheme, isDark } = useTheme();

  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      setSuccessMsg("🎉 Account created successfully! Please enter your password to sign in.");
      const emailParam = searchParams.get("email");
      if (emailParam) {
        setEmail(emailParam);
      }
    }
  }, [searchParams]);

  const getModuleTitle = (path) => {
    switch (path) {
      case "/profile": return "Module 1: Student Profile & Resumes";
      case "/resume-parser": return "Module 2: Deep Resume Parsing";
      case "/knowledge-base": return "Module 3: Internship Opportunities";
      case "/job-matching": return "Module 4: Job-Resume Matching";
      case "/skill-gap": return "Module 5: Skill Gap Analysis";
      case "/customizer": return "Module 6: Resume & Cover Customization";
      case "/interview-prep": return "Module 7: Interview Preparation";
      case "/career-assistant": return "Module 8: AI Career Assistant";
      default: return null;
    }
  };

  const handleLogin = async (e) => {
    e?.preventDefault();
    if (!email.trim() || !password) return;

    setLoading(true);
    setErrorMsg("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", email.trim());
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const user = response.data.user ?? response.data;
      const token = response.data.access_token;

      if (!token) throw new Error("No token received.");

      localStorage.setItem("access_token", token);
      if (user?.id != null) localStorage.setItem("user_id", String(user.id));
      if (user?.name) localStorage.setItem("user_name", user.name);
      if (user?.email) localStorage.setItem("user_email", user.email);
      if (user?.role) localStorage.setItem("user_role", user.role);

      navigate(redirectPath, { replace: true });
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "Invalid email or password. Please try again.";
      setErrorMsg(message);
    } finally {
      setLoading(false);
    }
  };

  const fillDemoAccount = async () => {
    const demoEmail = "arun.student@example.com";
    const demoPassword = "Student123!";
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrorMsg("");

    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append("username", demoEmail);
      formData.append("password", demoPassword);

      const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const user = response.data.user ?? response.data;
      const token = response.data.access_token;

      if (!token) throw new Error("No token received.");

      localStorage.setItem("access_token", token);
      if (user?.id != null) localStorage.setItem("user_id", String(user.id));
      if (user?.name) localStorage.setItem("user_name", user.name);
      if (user?.email) localStorage.setItem("user_email", user.email);
      if (user?.role) localStorage.setItem("user_role", user.role);

      navigate(redirectPath, { replace: true });
    } catch (err) {
      console.warn("Auto demo login note:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-wrapper">
      {/* LEFT SHOWCASE HERO */}
      <div className="auth-hero-pane">
        <div className="hero-pane-glow"></div>
        <div className="hero-pane-content">
          <Link to="/" className="hero-brand-link">
            <BrandLogo size="lg" showBadge={true} inverted={true} />
          </Link>

          <h1 className="hero-pane-title">
            Land Your Dream Internship with <span>Autonomous AI</span>.
          </h1>

          <p className="hero-pane-desc">
            Your personalized career launchpad: semantic RAG job matching, real-time resume ATS optimization, STAR behavioral interview coaching, and continuous AI mentorship.
          </p>

          {/* Floating UI Feature Cards */}
          <div className="hero-feature-cards">
            <div className="h-card">
              <div className="h-card-icon">🎯</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>Compatibility Score: 94%</strong>
                  <span className="badge-match-h">Top Match</span>
                </div>
                <small>Matched: Python, FastAPI, Docker, SQL, Git</small>
              </div>
            </div>

            <div className="h-card">
              <div className="h-card-icon">🎙️</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>Mock Interview Evaluator</strong>
                  <span className="badge-score-h">Score: 9/10</span>
                </div>
                <small>"Strong non-blocking I/O explanation with async loop metrics."</small>
              </div>
            </div>

            <div className="h-card">
              <div className="h-card-icon">💼</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>Internship Opportunities</strong>
                  <span className="badge-tech-h">Verified</span>
                </div>
                <small>12+ verified tech tracks with grounded domain intelligence</small>
              </div>
            </div>
          </div>

          <div className="hero-stats-strip">
            <div className="stat-pill">
              <strong>9</strong>
              <span>Core Modules</span>
            </div>
            <div className="stat-pill">
              <strong>12+</strong>
              <span>Job Domains</span>
            </div>
            <div className="stat-pill">
              <strong>24/7</strong>
              <span>AI Mentorship</span>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT AUTH CARD PANE */}
      <div className="auth-form-pane">
        <div className="auth-card-modern">
          <div className="auth-card-top-nav">
            <Link to="/" className="auth-back-pill">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Home</span>
            </Link>
            <div className="auth-top-actions">
              <button
                type="button"
                onClick={toggleTheme}
                className="btn-auth-theme-pill"
                title={`Switch to ${isDark ? "Light" : "Dark"} Mode`}
                aria-label="Toggle Theme"
              >
                {isDark ? (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <span>Light</span>
                  </>
                ) : (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    <span>Dark</span>
                  </>
                )}
              </button>
              <span className="auth-secure-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <span>Secure</span>
              </span>
            </div>
          </div>

          <div className="auth-header-block">
            <h2>Welcome Back</h2>
            <p>Enter your credentials or test with one-click demo access</p>
          </div>

          {getModuleTitle(redirectPath) && (
            <div className="auth-target-banner">
              <span className="target-badge-icon">👉</span>
              <div>
                Please sign in to open: <strong>{getModuleTitle(redirectPath)}</strong>
              </div>
            </div>
          )}

          {successMsg && <div className="auth-alert-success">{successMsg}</div>}
          {errorMsg && <div className="auth-alert-error">{errorMsg}</div>}

          {/* Quick Demo Login Option */}
          <button
            type="button"
            onClick={fillDemoAccount}
            className="btn-demo-quickfill"
          >
            ⚡ Click to Fill Demo Student Credentials
          </button>

          <div className="auth-divider">
            <span>or sign in with email</span>
          </div>

          <form onSubmit={handleLogin} className="auth-form-clean">
            <div className="input-group-modern">
              <label htmlFor="login-email">Email Address</label>
              <div className="input-with-icon">
                <span className="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </span>
                <input
                  id="login-email"
                  type="email"
                  placeholder="name@university.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="input-group-modern">
              <div className="label-row-between">
                <label htmlFor="login-password">Password</label>
                <Link to="/forgot-password" className="link-forgot">
                  Forgot password?
                </Link>
              </div>
              <div className="input-with-icon">
                <span className="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </span>
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="btn-toggle-eye"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-auth-gradient" disabled={loading}>
              {loading ? (
                <span className="btn-loading-flex">
                  <span className="spinner-sm"></span> Signing In...
                </span>
              ) : (
                "Sign In to Portal →"
              )}
            </button>
          </form>

          <div className="auth-footer-block">
            <p>
              Don't have an account?{" "}
              <Link
                to={`/register${redirectPath !== "/dashboard" ? `?redirect=${encodeURIComponent(redirectPath)}` : ""}`}
                className="auth-link-bold"
              >
                Create Free Account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}


// Reusable Enterprise Password Criteria & Strength Checklist
function PasswordCriteriaChecklist({ password = "", confirmPassword = null, showConfirm = false }) {
  const criteria = [
    {
      id: "length",
      label: "At least 8 characters",
      met: password.length >= 8,
      sublabel: password.length > 0 ? `${password.length}/8` : ""
    },
    {
      id: "upper",
      label: "At least 1 uppercase letter (A-Z)",
      met: /[A-Z]/.test(password)
    },
    {
      id: "lower",
      label: "At least 1 lowercase letter (a-z)",
      met: /[a-z]/.test(password)
    },
    {
      id: "number",
      label: "At least 1 numeric digit (0-9)",
      met: /[0-9]/.test(password)
    },
    {
      id: "special",
      label: "At least 1 special symbol (!@#$%^&*...)",
      met: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~`"'/\\]/.test(password)
    },
    {
      id: "no_space",
      label: "No spaces allowed",
      met: !/\s/.test(password) && password.length > 0
    }
  ];

  if (showConfirm && confirmPassword !== null) {
    criteria.push({
      id: "match",
      label: "Passwords match exactly",
      met: password.length > 0 && password === confirmPassword
    });
  }

  const metCount = criteria.filter((c) => c.met).length;
  const totalCount = criteria.length;
  const percent = Math.round((metCount / totalCount) * 100);

  let strengthLabel = "Too Weak";
  let strengthColor = "#ef4444";
  if (metCount <= 2) {
    strengthLabel = "Weak";
    strengthColor = "#ef4444";
  } else if (metCount <= 4) {
    strengthLabel = "Fair";
    strengthColor = "#f59e0b";
  } else if (metCount < totalCount) {
    strengthLabel = "Good";
    strengthColor = "#3b82f6";
  } else {
    strengthLabel = "Strong & Compliant ✓";
    strengthColor = "#10b981";
  }

  return (
    <div className="pwd-criteria-card">
      <div className="pwd-strength-header">
        <span className="pwd-strength-title">Security Criteria Checklist:</span>
        <span className="pwd-strength-status" style={{ color: strengthColor, fontWeight: "700" }}>
          {strengthLabel} ({metCount}/{totalCount})
        </span>
      </div>

      <div className="pwd-meter-track">
        <div
          className="pwd-meter-fill"
          style={{ width: `${percent}%`, backgroundColor: strengthColor }}
        ></div>
      </div>

      <div className="pwd-criteria-grid">
        {criteria.map((c) => (
          <div
            key={c.id}
            className={`pwd-criterion-item ${c.met ? "criterion-met" : "criterion-unmet"}`}
          >
            <span className="criterion-icon">{c.met ? "✓" : "✕"}</span>
            <span className="criterion-text">{c.label}</span>
            {c.sublabel && <small className="criterion-sub">({c.sublabel})</small>}
          </div>
        ))}
      </div>
    </div>
  );
}


export function Register() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectPath = "/dashboard";

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const { theme, toggleTheme, isDark } = useTheme();

  // Real-time criteria validation
  const isLengthValid = password.length >= 8 && password.length <= 128;
  const isUpperValid = /[A-Z]/.test(password);
  const isLowerValid = /[a-z]/.test(password);
  const isNumberValid = /[0-9]/.test(password);
  const isSpecialValid = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~`"'/\\]/.test(password);
  const isNoSpaceValid = !/\s/.test(password) && password.length > 0;
  const isAllPasswordCriteriaMet =
    isLengthValid &&
    isUpperValid &&
    isLowerValid &&
    isNumberValid &&
    isSpecialValid &&
    isNoSpaceValid;

  const isGmail = email.trim().toLowerCase().endsWith("@gmail.com") || email.trim().toLowerCase().endsWith("@googlemail.com");

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    if (!name.trim()) {
      setErrorMsg("Please enter your name.");
      return;
    }
    if (!email.trim()) {
      setErrorMsg("Please enter your email.");
      return;
    }
    if (!password || password.length < 4) {
      setErrorMsg("Password must be at least 4 characters long.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/register", {
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password: password
      });

      // Redirect back to login page
      navigate(`/login?registered=true&email=${encodeURIComponent(email.trim().toLowerCase())}`, { replace: true });
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || "Registration failed. Please verify your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-wrapper">
      {/* LEFT HERO BRAND PANE */}
      <div className="auth-hero-pane">
        <div className="hero-pane-glow"></div>
        <div className="hero-pane-content">
          <Link to="/" className="hero-brand-link">
            <BrandLogo size="lg" showBadge={true} inverted={true} />
          </Link>

          <h1 className="hero-pane-title">
            Unlock 8 Autonomous AI Suites for <span>Student Success</span>.
          </h1>

          <p className="hero-pane-desc">
            Create your free student account to parse your resume, diagnose skill gaps, auto-tailor application materials, and practice role-specific technical interviews.
          </p>

          <div className="hero-feature-cards">
            <div className="h-card">
              <div className="h-card-icon">🚀</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>Zero Cost for Students</strong>
                  <span className="badge-match-h">100% Free</span>
                </div>
                <small>Full access to AI Mock Interviews & RAG Matching</small>
              </div>
            </div>

            <div className="h-card">
              <div className="h-card-icon">⚡</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>ATS Resume Customizer</strong>
                  <span className="badge-score-h">High Impact</span>
                </div>
                <small>Keyword enrichment & quantified bullet generation</small>
              </div>
            </div>

            <div className="h-card">
              <div className="h-card-icon">📋</div>
              <div className="h-card-body">
                <div className="h-card-header">
                  <strong>Kanban Tracking Board</strong>
                  <span className="badge-tech-h">Organized</span>
                </div>
                <small>Never miss an interview round or application deadline</small>
              </div>
            </div>
          </div>

          <div className="hero-stats-strip">
            <div className="stat-pill">
              <strong>22+</strong>
              <span>Internships</span>
            </div>
            <div className="stat-pill">
              <strong>100%</strong>
              <span>Verified ATS</span>
            </div>
            <div className="stat-pill">
              <strong>8</strong>
              <span>AI Suites</span>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT AUTH CARD PANE */}
      <div className="auth-form-pane">
        <div className="auth-card-modern">
          <div className="auth-card-top-nav">
            <Link to="/" className="auth-back-pill">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              <span>Home</span>
            </Link>
            <div className="auth-top-actions">
              <button
                type="button"
                onClick={toggleTheme}
                className="btn-auth-theme-pill"
                title={`Switch to ${isDark ? "Light" : "Dark"} Mode`}
                aria-label="Toggle Theme"
              >
                {isDark ? (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <span>Light</span>
                  </>
                ) : (
                  <>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    <span>Dark</span>
                  </>
                )}
              </button>
              <span className="auth-secure-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                <span>Instant Setup</span>
              </span>
            </div>
          </div>

          <div className="auth-header-block">
            <h2>Create Account</h2>
            <p>Join the next generation AI internship acceleration platform</p>
          </div>

          {errorMsg && <div className="auth-alert-error">⚠️ {errorMsg}</div>}

          <form onSubmit={handleRegister} className="auth-form-clean">
            <div className="input-group-modern">
              <label htmlFor="reg-name">Full Name</label>
              <div className="input-with-icon">
                <span className="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </span>
                <input
                  id="reg-name"
                  type="text"
                  placeholder="e.g. Arun"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="input-group-modern">
              <div className="label-row-between">
                <label htmlFor="reg-email">Gmail Address</label>
                {email && (
                  <span className={`email-format-badge ${isGmail ? "badge-valid" : "badge-warn"}`}>
                    {isGmail ? "✓ Valid Gmail" : "⚠️ Use @gmail.com"}
                  </span>
                )}
              </div>
              <div className="input-with-icon">
                <span className="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </span>
                <input
                  id="reg-email"
                  type="email"
                  placeholder="e.g. student@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="input-group-modern">
              <label htmlFor="reg-password">Password (Security Standard)</label>
              <div className="input-with-icon">
                <span className="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </span>
                <input
                  id="reg-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter strong password (e.g. Strong@2026!)"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="btn-toggle-eye"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                      <line x1="1" y1="1" x2="23" y2="23" />
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  )}
                </button>
              </div>

              {/* Real-time Interactive Password Criteria Checklist */}
              {password.length > 0 && (
                <PasswordCriteriaChecklist password={password} />
              )}
            </div>

            <button
              type="submit"
              className="btn-auth-gradient"
              disabled={loading || password.length < 4}
              title="Create Account"
            >
              {loading ? (
                <span className="btn-loading-flex">
                  <span className="spinner-sm"></span> Creating Account...
                </span>
              ) : (
                "Create Free Account →"
              )}
            </button>
          </form>

          <div className="auth-footer-block">
            <p>
              Already registered?{" "}
              <Link
                to={`/login${redirectPath !== "/dashboard" ? `?redirect=${encodeURIComponent(redirectPath)}` : ""}`}
                className="auth-link-bold"
              >
                Sign In to Portal
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ForgotPassword() {
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // OTP State
  const [otpStep, setOtpStep] = useState(1); // 1 = enter email, 2 = enter otp & new pwd
  const [generatedOtp, setGeneratedOtp] = useState("");
  const [enteredOtp, setEnteredOtp] = useState("");

  // Password fields
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const cleanEmail = email.trim().toLowerCase();
  const isGmail = cleanEmail.endsWith("@gmail.com") || cleanEmail.endsWith("@googlemail.com");

  // Real-time criteria validation
  const isLengthValid = newPassword.length >= 8 && newPassword.length <= 128;
  const isUpperValid = /[A-Z]/.test(newPassword);
  const isLowerValid = /[a-z]/.test(newPassword);
  const isNumberValid = /[0-9]/.test(newPassword);
  const isSpecialValid = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~`"'/\\]/.test(newPassword);
  const isNoSpaceValid = !/\s/.test(newPassword) && newPassword.length > 0;
  const isMatch = newPassword.length > 0 && newPassword === confirmPassword;

  const isAllCriteriaMet =
    isLengthValid &&
    isUpperValid &&
    isLowerValid &&
    isNumberValid &&
    isSpecialValid &&
    isNoSpaceValid &&
    isMatch;

  // Handle Send OTP
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError("");
    if (!cleanEmail) return;
    if (!isGmail) {
      setError("Password reset is strictly available ONLY for registered Gmail accounts (@gmail.com).");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/auth/send-otp", { email: cleanEmail });
      setGeneratedOtp(res.data.otp_code || "");
      setEnteredOtp(res.data.otp_code || ""); // auto-fill for instant convenience
      setOtpStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate verification code. Please check your registered Gmail address.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Verify OTP & Reset
  const handleVerifyOTPAndReset = async (e) => {
    e.preventDefault();
    setError("");
    if (!enteredOtp || enteredOtp.length !== 6) {
      setError("Please enter the complete 6-digit verification code.");
      return;
    }
    if (!isAllCriteriaMet) {
      setError(!isMatch ? "Passwords do not match." : "Password does not meet all security criteria.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/auth/verify-otp-reset", {
        email: cleanEmail,
        otp: enteredOtp.trim(),
        new_password: newPassword
      });
      setSuccessMsg(res.data.message || "Password updated successfully!");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed. Please check the code and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-wrapper">
      <div className="auth-hero-pane">
        <div className="hero-pane-glow"></div>
        <div className="hero-pane-content">
          <Link to="/" className="hero-brand-link">
            <BrandLogo size="lg" showBadge={true} inverted={true} />
          </Link>
          <h1 className="hero-pane-title">
            6-Digit Code <span>Reset</span>.
          </h1>
          <p className="hero-pane-desc">
            Enter your registered Gmail account to generate a secure 6-digit verification code and reset your password instantly.
          </p>
          <div style={{ marginTop: "24px", display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", color: "rgba(255,255,255,0.85)" }}>
              <span>⚡</span> <span><strong>Instant Verification</strong>: 6-digit code for instant verification</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", color: "rgba(255,255,255,0.85)" }}>
              <span>🛡️</span> <span><strong>Registered Gmail Only</strong>: Verified accounts only (@gmail.com)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", color: "rgba(255,255,255,0.85)" }}>
              <span>🔒</span> <span><strong>Enterprise Criteria</strong>: Uppercase, lowercase, numbers & symbols</span>
            </div>
          </div>
        </div>
      </div>

      <div className="auth-form-pane">
        <div className="auth-card-modern">
          <div className="auth-card-top-nav">
            <Link to="/login" className="auth-back-pill">
              ← Back to Sign In
            </Link>
            <span className="auth-secure-tag">🛡️ Registered Gmail Only</span>
          </div>

          <div className="auth-header-block">
            <h2>Reset Your Password</h2>
            <p>
              {otpStep === 1
                ? "Enter your registered Gmail account to receive your 6-digit verification code"
                : `Enter the 6-digit code generated for ${cleanEmail}`}
            </p>
          </div>

          {error && (
            <div className="alert-banner alert-error" style={{ marginBottom: "16px" }}>
              ⚠️ {error}
            </div>
          )}

          {successMsg && (
            <div style={{
              background: "#ecfdf5",
              border: "1px solid #6ee7b7",
              color: "#065f46",
              padding: "16px",
              borderRadius: "10px",
              textAlign: "center",
              marginBottom: "16px"
            }}>
              <div style={{ fontSize: "24px", marginBottom: "6px" }}>🎉</div>
              <strong style={{ fontSize: "15px" }}>{successMsg}</strong>
              <p style={{ margin: "6px 0 0", fontSize: "13px", color: "#047857" }}>
                Redirecting you to sign in...
              </p>
            </div>
          )}

          {!successMsg && (
            <div>
              {otpStep === 1 ? (
                <form onSubmit={handleSendOTP} className="auth-form-clean">
                  <div className="input-group-modern">
                    <div className="label-row-between">
                      <label htmlFor="otp-email">Registered Gmail Address *</label>
                      <span className="auth-hint-pill">🔒 @gmail.com only</span>
                    </div>
                    <div className="input-with-icon">
                      <span className="input-icon">✉️</span>
                      <input
                        id="otp-email"
                        type="email"
                        placeholder="e.g. arun@gmail.com"
                        value={email}
                        onChange={(e) => { setEmail(e.target.value); setError(""); }}
                        required
                        disabled={loading}
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-auth-gradient"
                    disabled={loading || (email.length > 0 && !isGmail)}
                  >
                    {loading ? "Generating Code..." : "Generate 6-Digit Code →"}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOTPAndReset} className="auth-form-clean">
                  <div style={{
                    background: "#fef3c7",
                    border: "1px solid #fcd34d",
                    borderRadius: "8px",
                    padding: "12px 14px",
                    marginBottom: "14px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between"
                  }}>
                    <div>
                      <div style={{ fontSize: "11px", color: "#92400e", fontWeight: "700", textTransform: "uppercase" }}>Your 6-Digit Code</div>
                      <div style={{ fontSize: "20px", fontWeight: "900", letterSpacing: "4px", color: "#78350f" }}>
                        {generatedOtp}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEnteredOtp(generatedOtp)}
                      style={{
                        background: "#f59e0b",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        padding: "6px 12px",
                        fontSize: "12px",
                        fontWeight: "700",
                        cursor: "pointer"
                      }}
                    >
                      ⚡ Auto-Fill
                    </button>
                  </div>

                  <div className="input-group-modern">
                    <label htmlFor="otp-input">Enter 6-Digit Verification Code *</label>
                    <input
                      id="otp-input"
                      type="text"
                      maxLength="6"
                      placeholder="e.g. 482910"
                      value={enteredOtp}
                      onChange={(e) => setEnteredOtp(e.target.value.replace(/\D/g, ""))}
                      style={{
                        letterSpacing: "6px",
                        fontSize: "18px",
                        fontWeight: "800",
                        textAlign: "center"
                      }}
                      required
                    />
                  </div>

                  <div className="input-group-modern">
                    <div className="label-row-between">
                      <label htmlFor="otp-pwd">New Password *</label>
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        style={{ background: "none", border: "none", color: "#4f46e5", fontSize: "12px", cursor: "pointer", fontWeight: "600" }}
                      >
                        {showPassword ? "Hide" : "Show"}
                      </button>
                    </div>
                    <input
                      id="otp-pwd"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter strong new password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                    />
                  </div>

                  <div className="input-group-modern">
                    <label htmlFor="otp-confirm-pwd">Confirm New Password *</label>
                    <input
                      id="otp-confirm-pwd"
                      type={showPassword ? "text" : "password"}
                      placeholder="Re-enter new password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>

                  {newPassword.length > 0 && (
                    <PasswordCriteriaChecklist
                      password={newPassword}
                      confirmPassword={confirmPassword}
                      showConfirm={true}
                    />
                  )}

                  <button
                    type="submit"
                    className="btn-auth-gradient"
                    disabled={loading || !isAllCriteriaMet || enteredOtp.length !== 6}
                  >
                    {loading ? "Verifying & Updating..." : "Verify Code & Reset Password →"}
                  </button>

                  <button
                    type="button"
                    onClick={() => setOtpStep(1)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "#64748b",
                      fontSize: "12px",
                      marginTop: "10px",
                      width: "100%",
                      cursor: "pointer"
                    }}
                  >
                    ← Change email or request new code
                  </button>
                </form>
              )}
            </div>
          )}

          <div className="auth-footer-block" style={{ marginTop: "20px" }}>
            <p>
              Remembered your password?{" "}
              <Link to="/login" className="auth-link-bold">
                Back to Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ResetPassword() {
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [verifyError, setVerifyError] = useState("");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState("");

  // Real-time criteria validation
  const isLengthValid = newPassword.length >= 8 && newPassword.length <= 128;
  const isUpperValid = /[A-Z]/.test(newPassword);
  const isLowerValid = /[a-z]/.test(newPassword);
  const isNumberValid = /[0-9]/.test(newPassword);
  const isSpecialValid = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~`"'/\\]/.test(newPassword);
  const isNoSpaceValid = !/\s/.test(newPassword) && newPassword.length > 0;
  const isMatch = newPassword.length > 0 && newPassword === confirmPassword;

  const isAllPasswordCriteriaMet =
    isLengthValid &&
    isUpperValid &&
    isLowerValid &&
    isNumberValid &&
    isSpecialValid &&
    isNoSpaceValid &&
    isMatch;

  useEffect(() => {
    if (!token) {
      setVerifying(false);
      setTokenValid(false);
      setVerifyError("No reset token provided. Please request a new password reset link from your registered Gmail.");
      return;
    }

    const verifyToken = async () => {
      try {
        const res = await api.post("/auth/verify-reset-token", { token });
        setUserInfo(res.data);
        setTokenValid(true);
      } catch (err) {
        setTokenValid(false);
        setVerifyError(err.response?.data?.detail || "Invalid or expired password reset link. Please request a new one.");
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleReset = async (e) => {
    e.preventDefault();
    setSubmitError("");

    if (!isAllPasswordCriteriaMet) {
      if (!isMatch) {
        setSubmitError("Passwords do not match. Please ensure both fields are identical.");
      } else {
        setSubmitError("Password does not satisfy all required security criteria.");
      }
      return;
    }

    setSubmitting(true);
    try {
      await api.post("/auth/reset-password", {
        token,
        new_password: newPassword
      });
      setSubmitSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 2500);
    } catch (err) {
      setSubmitError(err.response?.data?.detail || "Failed to update password. The reset link may have expired.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-split-wrapper">
      <div className="auth-hero-pane">
        <div className="hero-pane-glow"></div>
        <div className="hero-pane-content">
          <Link to="/" className="hero-brand-link">
            <BrandLogo size="lg" showBadge={true} inverted={true} />
          </Link>
          <h1 className="hero-pane-title">
            Choose a New <span>Password</span>.
          </h1>
          <p className="hero-pane-desc">
            Keep your account secure with enterprise-grade password criteria. Your new password will grant immediate access to your candidate profile and all 8 modules.
          </p>
        </div>
      </div>

      <div className="auth-form-pane">
        <div className="auth-card-modern">
          <div className="auth-card-top-nav">
            <Link to="/login" className="auth-back-pill">
              ← Back to Sign In
            </Link>
            <span className="auth-secure-tag">🛡️ Verified Session</span>
          </div>

          <div className="auth-header-block">
            <h2>Set New Password</h2>
            {userInfo?.email ? (
              <p>
                Updating credentials for registered Gmail: <strong>{userInfo.email}</strong>
              </p>
            ) : (
              <p>Enter your new compliant password below</p>
            )}
          </div>

          {verifying ? (
            <div style={{ textAlign: "center", padding: "40px 0" }}>
              <div className="auth-spinner" style={{ margin: "0 auto 16px" }}></div>
              <p style={{ color: "#64748b", fontSize: "14px" }}>Verifying reset security token...</p>
            </div>
          ) : !tokenValid ? (
            <div className="direct-reset-card" style={{ textAlign: "center" }}>
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>⚠️</div>
              <h3 style={{ margin: "0 0 8px", color: "#0f172a", fontSize: "18px" }}>Reset Link Expired or Invalid</h3>
              <p style={{ color: "#ef4444", fontSize: "13.5px", margin: "0 0 20px" }}>{verifyError}</p>
              <Link to="/forgot-password" className="btn-auth-gradient" style={{ display: "inline-block", textDecoration: "none" }}>
                Request New Reset Link →
              </Link>
            </div>
          ) : submitSuccess ? (
            <div className="direct-reset-card" style={{ textAlign: "center" }}>
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>🎉</div>
              <h3 style={{ margin: "0 0 8px", color: "#0f172a", fontSize: "18px" }}>Password Reset Complete!</h3>
              <p style={{ color: "#10b981", fontSize: "13.5px", margin: "0 0 20px" }}>
                Your account password has been updated securely. Redirecting you to sign in...
              </p>
              <Link to="/login" className="btn-auth-gradient" style={{ display: "inline-block", textDecoration: "none" }}>
                Sign In Now →
              </Link>
            </div>
          ) : (
            <form onSubmit={handleReset} className="auth-form-clean">
              {submitError && (
                <div className="alert-banner alert-error" style={{ marginBottom: "16px" }}>
                  ⚠️ {submitError}
                </div>
              )}

              <div className="input-group-modern">
                <label htmlFor="new-password">New Password</label>
                <div className="input-with-icon">
                  <span className="input-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                  </span>
                  <input
                    id="new-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter new password (min 8 chars)"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    disabled={submitting}
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>

                {/* Real-time Checklist for New Password */}
                {newPassword.length > 0 && (
                  <PasswordCriteriaChecklist
                    password={newPassword}
                    confirmPassword={confirmPassword}
                    showConfirm={confirmPassword.length > 0}
                  />
                )}
              </div>

              <div className="input-group-modern">
                <div className="label-row-between">
                  <label htmlFor="confirm-password">Confirm New Password</label>
                  {confirmPassword.length > 0 && (
                    <span className={`pwd-match-badge ${isMatch ? "match-yes" : "match-no"}`}>
                      {isMatch ? "✓ Passwords Match" : "✕ Do Not Match"}
                    </span>
                  )}
                </div>
                <div className="input-with-icon">
                  <span className="input-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                  </span>
                  <input
                    id="confirm-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Repeat your new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={submitting}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="btn-auth-gradient"
                disabled={submitting || newPassword.length < 4}
                title="Update Password"
              >
                {submitting ? (
                  <span className="btn-loading-flex">
                    <span className="spinner-sm"></span> Updating Password...
                  </span>
                ) : (
                  "Update Password & Sign In →"
                )}
              </button>
            </form>
          )}

          <div className="auth-footer-block">
            <p>
              Remembered your credentials?{" "}
              <Link to="/login" className="auth-link-bold">
                Back to Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
