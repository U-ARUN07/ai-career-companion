import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import FloatingAICopilot from "./FloatingAICopilot";
import BrandLogo from "./BrandLogo";
import { useTheme } from "../context/ThemeContext";
import api from "../services/api";

const MODULE_CONFIG = {
  "/dashboard": { id: "00", name: "Command Cockpit", color: "#0d9488", icon: "📊" },
  "/profile": { id: "01", name: "Candidate Profile", color: "#0284c7", icon: "👤" },
  "/resume-parser": { id: "02", name: "Deep ATS Parser", color: "#0891b2", icon: "📄" },
  "/knowledge-base": { id: "03", name: "Internship Radar", color: "#2563eb", icon: "💼" },
  "/job-matching": { id: "04", name: "Semantic Matching", color: "#e11d48", icon: "🎯" },
  "/skill-gap": { id: "05", name: "Skill Gap Studio", color: "#d97706", icon: "📈" },
  "/customizer": { id: "06", name: "Resume & CV Architect", color: "#db2777", icon: "📝" },
  "/interview-prep": { id: "07", name: "Mock Simulator", color: "#059669", icon: "🎙️" },
  "/career-assistant": { id: "08", name: "AI Career Copilot", color: "#0ea5e9", icon: "🤖" },
};

export default function Layout({ children, title, subtitle }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme, isDark } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [userName, setUserName] = useState(() => localStorage.getItem("user_name") || "Arun");
  const userRole = localStorage.getItem("user_role") || "Intern";
  const avatar = (userName || "A").charAt(0).toUpperCase();

  useEffect(() => {
    const handleUpdate = (e) => {
      if (e.detail?.name) {
        setUserName(e.detail.name);
      }
    };
    const handleStorage = () => {
      setUserName(localStorage.getItem("user_name") || "Arun");
    };

    window.addEventListener("candidate_data_updated", handleUpdate);
    window.addEventListener("storage", handleStorage);

    const token = localStorage.getItem("access_token");
    if (token) {
      api.get("/api/profile/me").then((res) => {
        if (res.data?.name) {
          const cleanName = (res.data.name.toLowerCase().includes("aruna") || res.data.name.toLowerCase().includes("katravath") || res.data.name.toLowerCase().includes("rakesh")) ? "Arun" : res.data.name;
          setUserName(cleanName);
          localStorage.setItem("user_name", cleanName);
        }
      }).catch(() => {});
    }

    return () => {
      window.removeEventListener("candidate_data_updated", handleUpdate);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const activeMod = MODULE_CONFIG[location.pathname] || {
    id: "AI",
    name: "AI Career Companion",
    color: "#0d9488",
    icon: "⚡"
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_role");
    navigate("/login", { replace: true });
  };

  return (
    <div className="app">
      {/* Mobile Backdrop when Sidebar Drawer is open */}
      {sidebarOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar with open/close handlers */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="main">
        {/* Modern Responsive In-App Header */}
        <header className="topbar">
          <div className="topbar-left-wrap">
            <button
              type="button"
              className="btn-hamburger"
              onClick={() => setSidebarOpen((prev) => !prev)}
              aria-label="Toggle Navigation Menu"
              title="Toggle Menu"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>

            <div
              className="topbar-module-badge"
              style={{
                color: activeMod.color,
                backgroundColor: `${activeMod.color}15`,
                borderColor: `${activeMod.color}35`,
              }}
              title={`Active Module ${activeMod.id}: ${activeMod.name}`}
            >
              <span className="topbar-mod-emoji">{activeMod.icon}</span>
              <span className="topbar-mod-tag">MOD-{activeMod.id}</span>
            </div>

            <div className="topbar-title-block">
              <div className="topbar-title-row">
                <h2 title={title}>{title || "AI Career Companion"}</h2>
                <span className="topbar-active-pill">🟢 Live</span>
              </div>
              <p title={subtitle}>{subtitle || "Intelligent Career & Internship Accelerator"}</p>
            </div>
          </div>

          <div className="topbar-actions-block">
            {/* Tailored Topbar Theme Toggle Button */}
            <button
              type="button"
              onClick={toggleTheme}
              className="btn-theme-topbar"
              title={`Switch to ${isDark ? "Light" : "Dark"} Mode`}
              aria-label="Toggle Theme"
            >
              {isDark ? (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
              ) : (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
              )}
              <span className="btn-theme-topbar-label">{isDark ? "Light" : "Dark"}</span>
            </button>

            <div className="ai-status-indicator" title="Groq LLaMA-3.3 Intelligence Engine Connected">
              <span className="ai-status-pulse" style={{ flexShrink: 0 }}></span>
              <span className="ai-status-label">AI Ready</span>
            </div>

            <Link to="/career-assistant" className="btn-quick-assistant" title="Open Conversational Career Assistant">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
              <span className="btn-quick-assistant-label">Ask AI Mentor</span>
            </Link>

            <div className="user-profile-widget">
              <Link to="/profile" className="user-profile-widget-link" title="Click to view & edit your profile, email, and password">
                <div className="avatar" style={{ flexShrink: 0 }}>{avatar}</div>
                <div className="user-info-text">
                  <strong>{userName}</strong>
                  <small className="user-edit-profile-hint">✏️ Edit Profile</small>
                </div>
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="btn-topbar-logout"
                title="Sign out of account"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="page-content">{children}</div>

        {/* Modern Responsive In-App Footer */}
        <footer className="app-footer">
          <div className="app-footer-content">
            <div className="app-footer-left">
              <BrandLogo size="sm" showBadge={false} to="/dashboard" />
              <span className="footer-dot">•</span>
              <span className="app-footer-copy">© 2026 AI Career Companion Platform.</span>
            </div>

            <div className="app-footer-center">
              <span className="footer-engine-tag">
                <span className="engine-dot"></span> 8 Core Modules Active
              </span>
            </div>

            <div className="app-footer-links">
              <Link to="/knowledge-base">Internship Opportunities</Link>
              <Link to="/job-matching">Matching</Link>
              <Link to="/skill-gap">Skill Gap</Link>
              <Link to="/customizer">CV Generator</Link>
              <Link to="/interview-prep">Interview Prep</Link>
              <Link to="/career-assistant">AI Career Companion</Link>
            </div>
          </div>
        </footer>
      </main>

      {/* Floating AI Assistant at Right Corner (hidden when on full Career Assistant studio) */}
      {location.pathname !== "/career-assistant" && <FloatingAICopilot />}
    </div>
  );
}

