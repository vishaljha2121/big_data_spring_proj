import React from "react";

export default function ProgressBar({ value, color = "var(--purple)" }) {
  const safe = Math.max(0, Math.min(100, Number(value || 0)));
  return (
    <div className="progress-track">
      <span style={{ width: `${safe}%`, backgroundColor: color }} />
    </div>
  );
}
