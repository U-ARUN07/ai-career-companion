import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import BrandLogo from "./BrandLogo";
import api from "../services/api";

// Unique Modern Vector Icons for Each Module
function IconDashboard() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </svg>
  );
}

function IconProfile() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2.5" />
      <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2" />
      <circle cx="12" cy="13.5" r="1.5" fill="currentColor" />
      <path d="M2 13c4.5 1.5 15.5 1.5 20 0" />
    </svg>
  );
}

function IconJobMatching() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 10a7 7 0 0 0 14 0" />
      <line x1="12" y1="17" x2="12" y2="21" />
      <line x1="8" y1="21" x2="16" y2="21" />
    </svg>
  );
}


function IconAIMentor() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l2.2 5.3L20 9.5l-4.3 3.8 1.3 5.7L12 16l-5 3 1.3-5.7L4 9.5l5.8-2.2z" fill="currentColor" fillOpacity="0.18" />
      <path d="M19 16l1 2.5 2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1z" fill="currentColor" />
    </svg>
  );
}

export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [userName, setUserName] = useState(() => localStorage.getItem("user_name") || "Arun");
  const [targetRole, setTargetRole] = useState(() => localStorage.getItem("target_role") || "Full-Stack AI Engineer");
  const avatar = (userName || "A").charAt(0).toUpperCase();

  useEffect(() => {
    const handleUpdate = (e) => {
      if (e.detail?.name) {
        setUserName(e.detail.name);
      }
      if (e.detail?.target_role) {
        setTargetRole(e.detail.target_role);
      }
    };
    const handleStorage = () => {
      setUserName(localStorage.getItem("user_name") || "Arun");
      setTargetRole(localStorage.getItem("target_role") || "Full-Stack AI Engineer");
    };

    window.addEventListener("candidate_data_updated", handleUpdate);
    window.addEventListener("storage", handleStorage);

    const token = localStorage.getItem("access_token");
    if (token) {
      api.get("/api/profile/me").then((res) => {
        if (res.data?.name) {
          const clean = (res.data.name.toLowerCase().includes("aruna") || res.data.name.toLowerCase().includes("katravath") || res.data.name.toLowerCase().includes("rakesh")) ? "Arun" : res.data.name;
          setUserName(clean);
          localStorage.setItem("user_name", clean);
        }
        if (res.data?.target_role) {
          setTargetRole(res.data.target_role);
          localStorage.setItem("target_role", res.data.target_role);
        }
      }).catch(() => {});
    }

    return () => {
      window.removeEventListener("candidate_data_updated", handleUpdate);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
    if (onClose) onClose();
    navigate("/login", { replace: true });
  };

  const navSuites = [
    {
      suiteTitle: "TALENT INTELLIGENCE",
      items: [
        {
          path: "/dashboard",
          label: "Command Cockpit",
          id: "00",
          color: "#0d9488",
          icon: <IconDashboard />,
        },
        {
          path: "/profile",
          label: "Candidate Profile",
          id: "01",
          color: "#0284c7",
          icon: <IconProfile />,
        },
        {
          path: "/resume-parser",
          label: "Deep ATS Parser",
          id: "02",
          color: "#0891b2",
          icon: <IconResumeParser />,
        },
      ]
    },
    {
      suiteTitle: "MATCHING & GAPS",
      items: [
        {
          path: "/knowledge-base",
          label: "Internship Radar",
          id: "03",
          color: "#2563eb",
          icon: <IconOpportunities />,
        },
        {
          path: "/job-matching",
          label: "Semantic Matching",
          id: "04",
          color: "#e11d48",
          icon: <IconJobMatching />,
        },
        {
          path: "/skill-gap",
          label: "Skill Gap Studio",
          id: "05",
          color: "#d97706",
          icon: <IconSkillGap />,
        },
      ]
    },
    {
      suiteTitle: "CAREER ACCELERATION",
      items: [
        {
          path: "/customizer",
          label: "Resume & CV Architect",
          id: "06",
          color: "#db2777",
          icon: <IconCVBuilder />,
        },
        {
          path: "/interview-prep",
          label: "Mock Simulator",
          id: "07",
          color: "#059669",
          icon: <IconInterviewPrep />,
        },
        {
          path: "/career-assistant",
          label: "AI Career Copilot",
          id: "08",
          color: "#0ea5e9",
          icon: <IconAIMentor />,
        },
      ]
    }
  ];

  const { theme, toggleTheme, isDark } = useTheme();

  const handleNavClick = () => {
    if (onClose) onClose();
  };

  return (
    <aside className={`sidebar sidebar-modern ${isOpen ? "sidebar-open" : ""}`}>
      {/* Brand Header with Live Agent Pulse */}
      <div className="logo-section">
        <div className="logo-header-row">
          <Link to="/dashboard" onClick={handleNavClick} className="sidebar-brand-anchor" style={{ textDecoration: "none" }}>
            <BrandLogo size="sm" showBadge={true} />
          </Link>
          {onClose && (
            <button
              type="button"
              className="btn-sidebar-close"
              onClick={onClose}
              aria-label="Close Sidebar"
            >
              ✕
            </button>
          )}
        </div>

        <div className="sidebar-live-tag">
          <span className="live-dot-pulse"></span>
          <span>Autonomous Career Operating System</span>
        </div>
      </div>

      {/* Categorized Multi-Suite Nav Hierarchy */}
      <nav className="sidebar-nav">
        {navSuites.map((suite, sIdx) => (
          <div key={sIdx} className="nav-suite-group">
            <div className="nav-suite-header">
              <span className="nav-suite-label">{suite.suiteTitle}</span>
              <span className="nav-suite-count">{suite.items.length}</span>
            </div>
            <div className="nav-items-list">
              {suite.items.map((item) => {
                const isActive = location.pathname === item.path;
                const isMentor = item.id === "08";
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={handleNavClick}
                    className={`nav-link ${isActive ? "active" : ""} ${
                      isMentor ? "nav-link-mentor" : ""
                    }`}
                  >
                    <span
                      className="nav-unique-icon-box"
                      style={{
                        color: item.color,
                        backgroundColor: isActive ? `${item.color}22` : `${item.color}10`,
                        borderColor: isActive ? `${item.color}55` : `${item.color}22`,
                      }}
                      aria-hidden="true"
                    >
                      {item.icon}
                    </span>
                    <span className="nav-label">{item.label}</span>
                    <span className={`nav-uid-badge ${isMentor ? "nav-uid-badge-mentor" : ""}`}>
                      {item.id}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Compact User Bar with Placement Readiness & Theme Switcher */}
      <div className="sidebar-bottom">
        <div className="sidebar-readiness-widget">
          <div className="readiness-header-row">
            <span className="readiness-label">🎯 Placement Readiness</span>
            <span className="readiness-score-tag">94%</span>
          </div>
          <div className="readiness-track">
            <div className="readiness-fill" style={{ width: "94%" }}></div>
          </div>
          <div className="readiness-sub-text">
            <span>Verified Role: {targetRole || "Software Engineer Intern"}</span>
          </div>
        </div>

        <div className="sidebar-theme-wrapper">
          <button
            type="button"
            onClick={toggleTheme}
            className="sidebar-theme-toggle-btn"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
            aria-label="Toggle Theme"
          >
            <span className="theme-icon-badge">{theme === "dark" ? "☀️" : "🌙"}</span>
            <div className="theme-toggle-labels">
              <span className="theme-name-label">{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
              <small className="theme-state-sub">{theme === "dark" ? "Active: Dark Mode" : "Active: Light Mode"}</small>
            </div>
            <span className={`theme-mode-pill ${theme === "dark" ? "pill-dark" : "pill-light"}`}>
              {theme === "dark" ? "Dark" : "Light"}
            </span>
          </button>
        </div>

        <div className="sidebar-user-block">
          <Link to="/profile" onClick={handleNavClick} className="sidebar-user-card" title="Click to edit profile, email, and password">
            <div className="s-user-avatar">{avatar}</div>
            <div className="s-user-meta">
              <strong className="s-user-name">{userName}</strong>
              <small className="s-user-role">✏️ Candidate Portal</small>
            </div>
          </Link>

          <button
            type="button"
            onClick={logout}
            className="sidebar-logout-btn-clean"
            title="Sign out of your account"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
