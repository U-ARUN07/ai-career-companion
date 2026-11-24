import React from "react";
import { Link } from "react-router-dom";

/**
 * Unified, Pixel-Perfect Brand Logo for AI Career Companion
 * Guarantees identical typography, gradient bolt, consistent colors, 
 * and explicit non-collapsing spacing across all pages, footers, and headers.
 */
export default function BrandLogo({ size = "md", showBadge = false, className = "", to = null, inverted = false }) {
  const content = (
    <div className={`brand-logo-root brand-size-${size} ${inverted ? "brand-logo-inverted" : ""} ${className}`}>
      <div className="brand-logo-icon" aria-hidden="true">
        <span className="brand-logo-bolt">⚡</span>
      </div>
      <div className="brand-logo-text">
        <span 
          className="brand-text-career"
          style={{
            fontWeight: 800,
            color: inverted ? "#ffffff" : "var(--brand-career-color, #0f172a)",
            WebkitTextFillColor: inverted ? "#ffffff" : "var(--brand-career-color, #0f172a)"
          }}
        >
          AI Career
        </span>
        <span 
          className="brand-text-companion"
          style={{
            fontWeight: 800,
            color: "var(--brand-companion-color, #0d9488)",
            WebkitTextFillColor: "var(--brand-companion-color, #0d9488)"
          }}
        >
          Companion
        </span>
      </div>
      {showBadge && (
        <span className="brand-logo-badge">Agent</span>
      )}
    </div>
  );

  if (to) {
    return (
      <Link to={to} className="brand-logo-link" style={{ textDecoration: "none" }}>
        {content}
      </Link>
    );
  }

  return content;
}
