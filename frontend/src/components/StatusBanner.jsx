import React from "react";

export default function StatusBanner({ health, ready, summary }) {
  const apiReady = health?.status === "ok" && ready?.status === "ready";
  const scoredCount = summary?.scored_event_count || 0;
  return (
    <section className={`status-banner ${apiReady ? "ready" : "degraded"}`}>
      <div>
        <p className="eyebrow">File-backed local demo API</p>
        <h1>Tennis Point Scoring Dashboard</h1>
        <p>Point-level probabilities, risk review signals, model metadata, and benchmark evidence.</p>
      </div>
      <div className="status-pill">
        <span className="dot" />
        <strong>{apiReady ? "READY" : "CHECK API"}</strong>
        <span>{scoredCount.toLocaleString()} scored events</span>
      </div>
    </section>
  );
}
