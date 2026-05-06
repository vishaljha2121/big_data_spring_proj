import React from "react";
import ThemeSwitcher from "../components/ThemeSwitcher.jsx";

export default function TopHeader({ activePage, onNavigate, apiReady, summary, theme, onThemeChange }) {
  return (
    <header className="top-header">
      <div>
        <div className="breadcrumb">
          <button type="button" onClick={() => onNavigate("Dashboard")}>Home</button>
          <span>/</span>
          <strong>{activePage}</strong>
        </div>
        <h2>{activePage}</h2>
      </div>
      <div className="top-actions">
        <ThemeSwitcher theme={theme} onThemeChange={onThemeChange} />
        <span className={`status-pill ${apiReady ? "ready" : "warn"}`}>{apiReady ? "API Ready" : "Check API"}</span>
        <span className="date-pill">{(summary?.scored_event_count || 0).toLocaleString()} scored events</span>
        <span className="avatar">CC</span>
      </div>
    </header>
  );
}
