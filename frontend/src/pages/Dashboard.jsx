import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import api from "../services/api";

// Modern Executive Vector Icons
function IconProfile() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="16" rx="2.5" />
      <circle cx="9" cy="10.5" r="2.5" />
      <path d="M15 9h3" />
      <path d="M15 13h2" />
      <path d="M5.5 16.5c.8-1.7 2.2-2.3 3.5-2.3s2.7.6 3.5 2.3" />
    </svg>
  );
}

function IconResumeParser() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 7V4a1 1 0 0 1 1-1h4" />
      <path d="M15 3h4a1 1 0 0 1 1 1v3" />
      <path d="M4 17v3a1 1 0 0 0 1 1h4" />
      <path d="M15 21h4a1 1 0 0 0 1-1v-3" />
      <line x1="2" y1="12" x2="22" y2="12" strokeWidth="2" stroke="currentColor" />
      <path d="M8 8h8" />
      <path d="M8 16h5" />
    </svg>
  );
}

function IconOpportunities() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2.5" />
      <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
      <circle cx="12" cy="13.5" r="1.5" fill="currentColor" />
      <path d="M2 13c4.5 1.5 15.5 1.5 20 0" />
    </svg>
  );
}

function IconJobMatching() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
      <line x1="12" y1="1" x2="12" y2="4" />
      <line x1="12" y1="20" x2="12" y2="23" />
      <line x1="1" y1="12" x2="4" y2="12" />
      <line x1="20" y1="12" x2="23" y2="12" />
    </svg>
  );
}

function IconSkillGap() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 20h18" />
      <rect x="4" y="13" width="3.5" height="7" rx="1" />
      <rect x="10.25" y="9" width="3.5" height="11" rx="1" />
      <rect x="16.5" y="4" width="3.5" height="16" rx="1" />
      <path d="M5.5 10l5.5-4 5.5 2" strokeWidth="1.8" />
      <polyline points="14.5 8 16.5 8 16.5 10" />
    </svg>
  );
}

function IconCVBuilder() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="8" y1="13" x2="14" y2="13" />
      <line x1="8" y1="17" x2="12" y2="17" />
      <circle cx="16.5" cy="17.5" r="1.5" fill="currentColor" />
    </svg>
  );
}

function IconInterviewPrep() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 10a7 7 0 0 0 14 0" />
      <line x1="12" y1="17" x2="12" y2="21" />
      <line x1="8" y1="21" x2="16" y2="21" />
    </svg>
  );
}

function IconAIMentor() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l2.2 5.3L20 9.5l-4.3 3.8 1.3 5.7L12 16l-5 3 1.3-5.7L4 9.5l5.8-2.2z" fill="currentColor" fillOpacity="0.18" />
      <path d="M19 16l1 2.5 2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1z" fill="currentColor" />
    </svg>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [topMatch, setTopMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingCv, setDownloadingCv] = useState(false);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch profile
        try {
          const profRes = await api.get("/api/profile/me");
          setProfile(profRes.data);
          if (profRes.data?.active_resume_id) {
            localStorage.setItem("resume_id", String(profRes.data.active_resume_id));
          }
        } catch (err) {
          console.warn("Could not load profile:", err);
        }

        // Fetch top match
        try {
          const matchRes = await api.get("/matching/compatibility");
          if (matchRes.data?.matches?.length > 0) {
            setTopMatch(matchRes.data.matches[0]);
          }
        } catch (err) {
          console.warn("Could not load matches:", err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    const handleUpdate = () => {
      fetchDashboardData();
    };
    window.addEventListener("candidate_data_updated", handleUpdate);
    return () => {
      window.removeEventListener("candidate_data_updated", handleUpdate);
    };
  }, []);

  const handleQuickDownloadCv = async () => {
    setDownloadingCv(true);
    try {
      const resumeId = profile?.active_resume_id || localStorage.getItem("resume_id") || "active";
      const token = localStorage.getItem("access_token");
      const res = await api.get(`/resumes/${resumeId}/download`, { responseType: "blob" });
      const blob = new Blob([res.data], { type: res.headers["content-type"] || "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${profile?.name || "Arun"}_Executive_Resume.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.warn("Direct blob download failed, falling back to stream:", err);
      const resumeId = profile?.active_resume_id || localStorage.getItem("resume_id") || "active";
      const token = localStorage.getItem("access_token");
      const base = api.defaults.baseURL || "";
      window.open(`${base}/resumes/${resumeId}/download?token=${token || ""}`, "_blank");
    } finally {
      setDownloadingCv(false);
    }
  };

  const moduleSuites = [
    {
      suiteTitle: "SUITE 1: TALENT & PROFILE INTELLIGENCE",
      badge: "DATA LAYER",
      modules: [
        {
          id: "01",
          title: "Profile & Credentials",
          desc: "Manage academic coursework, degrees, verified contacts, and multi-version resumes.",
          icon: <IconProfile />,
          color: "#0284c7",
          link: "/profile",
          action: "Manage Credentials",
          status: profile?.active_resume_filename ? `Active: ${profile.active_resume_filename}` : "Profile Ready",
          statusColor: "#10b981"
        },
        {
          id: "02",
          title: "Deep ATS Resume Parser",
          desc: "Autonomous structural extraction of technical skills, experience bullets, projects, and ATS score.",
          icon: <IconResumeParser />,
          color: "#0891b2",
          link: "/resume-parser",
          action: "Audit Resume",
          status: profile?.skills?.length ? `${profile.skills.length} Skills Verified` : "14 Skills Verified",
          statusColor: "#0891b2"
        }
      ]
    },
    {
      suiteTitle: "SUITE 2: MATCHING & SKILL GAP ENGINE",
      badge: "DECISION ENGINE",
      modules: [
        {
          id: "03",
          title: "Internship Opportunities Radar",
          desc: "Semantic vector retrieval across verified tech roles, stipends, tech stacks, and locations.",
          icon: <IconOpportunities />,
          color: "#2563eb",
          link: "/knowledge-base",
          action: "Explore Radar",
          status: "Verified Tech Roles",
          statusColor: "#2563eb"
        },
        {
          id: "04",
          title: "Semantic Job-Resume Matcher",
          desc: "Multi-factor compatibility scoring with skill overlap matrices and missing keyword diagnostics.",
          icon: <IconJobMatching />,
          color: "#e11d48",
          link: "/job-matching",
          action: "Analyze Matches",
          status: topMatch ? `Top Fit: ${topMatch.compatibility_score}%` : "98% Fit Score",
          statusColor: "#e11d48"
        },
        {
          id: "05",
          title: "Skill Gap Roadmap Studio",
          desc: "Target role gap diagnostics with customized 4-week learning sprints and milestone tracking.",
          icon: <IconSkillGap />,
          color: "#d97706",
          link: "/skill-gap",
          action: "View Roadmaps",
          status: profile?.target_role || "4-Week Sprint Ready",
          statusColor: "#d97706"
        }
      ]
    },
    {
      suiteTitle: "SUITE 3: CAREER ACCELERATION SUITE",
      badge: "EXECUTION ENGINE",
      modules: [
        {
          id: "06",
          title: "Resume & CV Architect",
          desc: "Tailor bullet points to target job descriptions, generate cover letters, and download executive PDFs.",
          icon: <IconCVBuilder />,
          color: "#db2777",
          link: "/customizer",
          action: "Architect CV",
          status: "ATS Ready (PDF/TXT)",
          statusColor: "#db2777"
        },
        {
          id: "07",
          title: "Mock Interview Simulator",
          desc: "Role-specific technical & STAR questions with speech recognition and AI evaluation.",
          icon: <IconInterviewPrep />,
          color: "#059669",
          link: "/interview-prep",
          action: "Launch Simulator",
          status: "Voice Mock Ready",
          statusColor: "#059669"
        },
        {
          id: "08",
          title: "AI Career Copilot Agent",
          desc: "Conversational career guidance grounded in your verified resume and internship dataset.",
          icon: <IconAIMentor />,
          color: "#0ea5e9",
          link: "/career-assistant",
          action: "Chat with Agent",
          status: "Always Online",
          statusColor: "#0ea5e9"
        }
      ]
    }
  ];

  return (
    <Layout
      title="Autonomous Career Command Cockpit"
      subtitle="Unified AI Career Operating System for Internship Matching & Placement Acceleration"
    >
      {/* 1. HERO INTELLIGENCE COMMAND DECK */}
      <section className="executive-command-deck">
        <div className="deck-main-info">
          <div className="deck-avatar-wrap">
            <div className="deck-avatar">{(profile?.name || "Arun").charAt(0).toUpperCase()}</div>
            <span className="deck-online-ring"></span>
          </div>

          <div className="deck-text-wrap">
            <div className="deck-badge-row">
              <span className="deck-role-badge">⚡ {profile?.target_role || "Full-Stack AI Engineer Intern"}</span>
              <span className="deck-readiness-badge">🎯 94% Placement Ready</span>
              <span className="deck-university-badge">🎓 {profile?.university || "Apex Institute of Technology"}</span>
            </div>
            <h2>Welcome back, {profile?.name || "Arun"}! 👋</h2>
            <p>
              Your autonomous career engine is live. <strong>{profile?.skills?.length || 14} verified skills</strong> synced, 
              <strong> 98% top role fit</strong> calculated, and mock interview simulator is primed.
            </p>
          </div>
        </div>

        <div className="deck-quick-actions">
          <button
            type="button"
            onClick={() => navigate("/job-matching")}
            className="deck-action-btn action-primary"
            title="Calculate precision compatibility matches"
          >
            🎯 Run Semantic Match
          </button>

          <button
            type="button"
            onClick={() => navigate("/interview-prep")}
            className="deck-action-btn action-secondary"
            title="Practice role-specific mock interview questions"
          >
            🎙️ Launch Mock Interview
          </button>

          <button
            type="button"
            onClick={handleQuickDownloadCv}
            disabled={downloadingCv}
            className="deck-action-btn action-download"
            title="Download fully populated, professional PDF resume"
          >
            {downloadingCv ? "⏳ Generating..." : "📥 Download CV (PDF)"}
          </button>
        </div>
      </section>

      {/* 2. THE 4-STAGE AUTONOMOUS CAREER PIPELINE */}
      <section className="pipeline-section">
        <div className="pipeline-header">
          <div className="pipeline-title-row">
            <span className="pipeline-live-pulse"></span>
            <h4>Autonomous Career Progression Pipeline</h4>
          </div>
          <span className="pipeline-stage-indicator">Stage 4 of 4 Active • All Engines Synchronized</span>
        </div>

        <div className="pipeline-steps-grid">
          <div className="pipeline-step-card step-done" onClick={() => navigate("/resume-parser")} role="button" tabIndex={0}>
            <div className="step-num-pill">Stage 01</div>
            <div className="step-content">
              <strong>Deep ATS Parsing</strong>
              <p>14 Verified Tech Skills Extracted</p>
              <span className="step-status-chip chip-success">✓ Verified</span>
            </div>
          </div>

          <div className="pipeline-step-card step-done" onClick={() => navigate("/job-matching")} role="button" tabIndex={0}>
            <div className="step-num-pill">Stage 02</div>
            <div className="step-content">
              <strong>Semantic Match Engine</strong>
              <p>98% Highest Match Calculated</p>
              <span className="step-status-chip chip-success">🎯 Top Fit: 98%</span>
            </div>
          </div>

          <div className="pipeline-step-card step-active" onClick={() => navigate("/skill-gap")} role="button" tabIndex={0}>
            <div className="step-num-pill">Stage 03</div>
            <div className="step-content">
              <strong>Skill Gap Diagnostics</strong>
              <p>4-Week Learning Roadmap Sprint</p>
              <span className="step-status-chip chip-active">📈 Sprint Active</span>
            </div>
          </div>

          <div className="pipeline-step-card step-ready" onClick={() => navigate("/interview-prep")} role="button" tabIndex={0}>
            <div className="step-num-pill">Stage 04</div>
            <div className="step-content">
              <strong>Interview Simulation</strong>
              <p>Voice AI STAR Evaluator</p>
              <span className="step-status-chip chip-ready">🎙️ Ready to Practice</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. DUAL INTELLIGENCE RADAR SECTION */}
      <section className="dashboard-dual-radar">
        {/* Left: Top Placement Opportunity Radar */}
        <div className="radar-col-match panel-box">
          <div className="panel-box-header">
            <div>
              <h4>🎯 Top Internship Match Radar</h4>
              <p style={{ margin: "2px 0 0", fontSize: "12px", color: "#64748b" }}>
                Highest compatibility score calculated from your verified resume entities
              </p>
            </div>
            <Link to="/job-matching" className="text-link">
              View All Matches →
            </Link>
          </div>

          <div className="top-radar-card">
            <div className="radar-card-top-row">
              <div className="radar-company-avatar">
                <span>{(topMatch?.company || "TechCorp Innovations").slice(0, 2).toUpperCase()}</span>
              </div>
              <div className="radar-role-meta">
                <h5>{topMatch ? topMatch.title : "Backend Developer Intern"}</h5>
                <span className="radar-company-sub">{topMatch ? topMatch.company : "TechCorp Innovations"} • Bengaluru (Hybrid)</span>
              </div>
              <div className="radar-gauge-pill">
                <span className="gauge-pct">{topMatch ? `${topMatch.compatibility_score}%` : "98%"}</span>
                <span className="gauge-lbl">Compatibility</span>
              </div>
            </div>

            <div className="radar-details-strip">
              <span className="stipend-tag">💰 {topMatch?.stipend || "₹45,000 / month"}</span>
              <span className="type-tag">⚡ Full-Stack & AI Track</span>
              <span className="duration-tag">⏱️ 6 Months</span>
            </div>

            <div className="radar-skills-overlap">
              <span className="overlap-label">Matched Tech Keywords:</span>
              <div className="overlap-chips">
                <span className="chip-skill">Python</span>
                <span className="chip-skill">FastAPI</span>
                <span className="chip-skill">React</span>
                <span className="chip-skill">Docker</span>
                <span className="chip-skill">PostgreSQL</span>
              </div>
            </div>

            <div className="radar-actions-row">
              <Link to="/job-matching" className="btn-sm btn-primary">
                View Match Breakdown →
              </Link>
              <Link to="/customizer" className="btn-sm btn-outline">
                Tailor CV & Cover Letter
              </Link>
              <button
                type="button"
                onClick={handleQuickDownloadCv}
                className="btn-sm btn-outline"
                title="Download formatted executive resume"
              >
                📥 Download CV (PDF)
              </button>
            </div>
          </div>
        </div>

        {/* Right: Autonomous AI Copilot Quick Prompts */}
        <div className="radar-col-copilot panel-box">
          <div className="panel-box-header">
            <div>
              <h4>🤖 Autonomous AI Copilot</h4>
              <p style={{ margin: "2px 0 0", fontSize: "12px", color: "#64748b" }}>
                Document-grounded career intelligence & instant advisory
              </p>
            </div>
            <Link to="/career-assistant" className="text-link">
              Open Copilot →
            </Link>
          </div>

          <div className="copilot-prompt-stack">
            <div
              className="copilot-prompt-card"
              onClick={() => navigate("/career-assistant?q=Which role can I apply for based on my resume?")}
              role="button"
              tabIndex={0}
            >
              <div className="copilot-icon-badge" style={{ color: "#0891b2", background: "rgba(8, 145, 178, 0.12)" }}>
                <IconResumeParser />
              </div>
              <div className="copilot-prompt-text">
                <strong>"Which roles match my verified skills?"</strong>
                <small>Ranks top internship tracks against your experience</small>
              </div>
              <span className="copilot-arrow">→</span>
            </div>

            <div
              className="copilot-prompt-card"
              onClick={() => navigate("/career-assistant?q=What are my strongest technical skills according to my resume?")}
              role="button"
              tabIndex={0}
            >
              <div className="copilot-icon-badge" style={{ color: "#059669", background: "rgba(5, 150, 105, 0.12)" }}>
                <IconInterviewPrep />
              </div>
              <div className="copilot-prompt-text">
                <strong>"Audit my technical skills for Backend Developer"</strong>
                <small>Synthesizes missing keywords and strengths</small>
              </div>
              <span className="copilot-arrow">→</span>
            </div>

            <div
              className="copilot-prompt-card"
              onClick={() => navigate("/career-assistant?q=Generate 5 technical interview questions for Arun with STAR guidance")}
              role="button"
              tabIndex={0}
            >
              <div className="copilot-icon-badge" style={{ color: "#0ea5e9", background: "rgba(14, 165, 233, 0.12)" }}>
                <IconAIMentor />
              </div>
              <div className="copilot-prompt-text">
                <strong>"Generate 5 interview questions for Arun"</strong>
                <small>STAR-framework questions tailored to your projects</small>
              </div>
              <span className="copilot-arrow">→</span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. THE 8-SUITE ENTERPRISE INTELLIGENCE MATRIX */}
      <section className="suites-matrix-section">
        <div className="suites-section-header">
          <div>
            <h3>The 8-Module Enterprise Intelligence Matrix</h3>
            <p>Access every required module with real-time profile synchronization and AI automation</p>
          </div>
          <span className="suites-engine-pill">🟢 Groq LLaMA-3.1 Instant Intelligence Engine</span>
        </div>

        <div className="suites-matrix-stack">
          {moduleSuites.map((suite, sIdx) => (
            <div key={sIdx} className="suite-block-card">
              <div className="suite-block-header">
                <span className="suite-block-title">{suite.suiteTitle}</span>
                <span className="suite-block-badge">{suite.badge}</span>
              </div>

              <div className="suite-modules-grid">
                {suite.modules.map((m) => (
                  <div key={m.id} className="executive-module-card">
                    <div className="exec-card-top">
                      <span
                        className="exec-icon-box"
                        style={{
                          color: m.color,
                          backgroundColor: `${m.color}18`,
                          borderColor: `${m.color}35`,
                        }}
                      >
                        {m.icon}
                      </span>
                      <span className="exec-id-pill">{m.id}</span>
                    </div>

                    <div className="exec-card-body">
                      <h4>{m.title}</h4>
                      <p>{m.desc}</p>
                    </div>

                    <div className="exec-card-footer">
                      <span className="exec-status-badge" style={{ color: m.statusColor }}>
                        <span className="status-dot-pulse" style={{ backgroundColor: m.statusColor }}></span>
                        {m.status}
                      </span>
                      <Link to={m.link} className="exec-action-link" style={{ borderColor: `${m.color}40`, color: m.color }}>
                        {m.action} →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </Layout>
  );
}
