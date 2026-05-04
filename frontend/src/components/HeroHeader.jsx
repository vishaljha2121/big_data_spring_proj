import React from "react";
import ThemeSwitcher from "./ThemeSwitcher.jsx";

export default function HeroHeader({ health, ready, summary, theme, onThemeChange, surfaceUnavailable }) {
  const apiReady = health?.status === "ok" && ready?.status === "ready";
  return (
    <header className="hero-panel" id="overview">
      <nav className="top-nav" aria-label="Dashboard sections">
        <span className="brand-mark">CourtIQ</span>
        <div>
          <a href="#overview">Overview</a>
          <a href="#matches">Matches</a>
          <a href="#risk">Risk</a>
          <a href="#model">Model</a>
          <a href="#benchmark">Benchmark</a>
        </div>
      </nav>
      <div className="hero-content">
        <div>
          <p className="eyebrow">Clay-court analytics control room</p>
          <h1>CourtIQ Tennis Scoring Dashboard</h1>
          <p className="hero-copy">
            Point-level probabilities, statistical risk review signals, model metadata,
            and benchmark evidence served from the local file-backed API.
          </p>
          <div className="disclaimer-row">
            <span>Point-level probability, not betting odds</span>
            <span>Risk score = statistical review signal</span>
            <span>File-backed local demo API</span>
          </div>
          {surfaceUnavailable ? (
            <p className="surface-note">Surface metadata unavailable for this sample; dashboard shown in clay-court demo theme.</p>
          ) : null}
        </div>
        <aside className="hero-aside">
          <div className={`readiness-badge ${apiReady ? "ready" : "degraded"}`}>
            <span className="pulse" />
            <strong>{apiReady ? "API Ready" : "Check API"}</strong>
            <small>{(summary?.scored_event_count || 0).toLocaleString()} scored events</small>
          </div>
          <ThemeSwitcher theme={theme} onThemeChange={onThemeChange} />
        </aside>
      </div>
    </header>
  );
}
