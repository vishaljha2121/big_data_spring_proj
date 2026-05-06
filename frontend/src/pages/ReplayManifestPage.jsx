import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function ReplayManifestPage({ data }) {
  const rows = [
    { cells: ["replay_manifest_v1.parquet", "Validated artifact", "1,917,672", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["sample_events.jsonl", "Dry-run sample", "1,000", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["point_event_schema.json", "Kafka event contract", "schema", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["Kafka runtime", "Local runtime validation", "not executed", <StatusBadge status="planned">Planned</StatusBadge>] },
  ];
  return (
    <Card title="Replay Manifest Viewer" eyebrow="Validated repo artifact; dedicated API endpoint planned">
      <p className="module-note">The replay manifest exists under `data/replay/manifests/`. The current API exposes scored events and match streams, not raw manifest metadata.</p>
      <DataTable columns={["Artifact", "Purpose", "Rows/Type", "Status"]} rows={rows} />
    </Card>
  );
}
