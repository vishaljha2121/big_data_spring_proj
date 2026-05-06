import React from "react";
import Card from "../components/Card.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function SurfaceAnalyticsPage() {
  return (
    <div className="two-column-page">
      <Card title="Surface Analytics" eyebrow="Blocked by source data">
        <p className="module-note">Surface metadata is unavailable in the current curated sample. The dashboard theme selector is visual only and must not be interpreted as true surface labels.</p>
        <div className="status-list">
          <p><span>Surface coverage</span><strong>0.0%</strong></p>
          <p><span>Surface-specific baselines</span><StatusBadge status="planned">Blocked</StatusBadge></p>
          <p><span>Theme selector</span><StatusBadge status="PASSED">Visual only</StatusBadge></p>
        </div>
      </Card>
      <Card title="Readiness">
        <p className="muted-copy">Surface analytics can be enabled after reliable match metadata is joined and validated.</p>
        <ProgressBar value={0} color="var(--gold)" />
      </Card>
    </div>
  );
}
