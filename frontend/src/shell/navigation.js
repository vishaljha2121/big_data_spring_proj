export const NAV_GROUPS = [
  {
    title: "Analytics",
    items: ["Dashboard", "Match Browser", "Players", "Player Comparison", "Tournaments", "Surface Analytics", "Rankings"],
  },
  {
    title: "Replay",
    items: ["Replay Center", "Point Timeline", "Replay Manifest"],
  },
  {
    title: "ML Model",
    items: ["Prediction Center", "Model Performance"],
  },
  {
    title: "Data Ops",
    items: ["Data Explorer", "Validation", "Pipeline Monitor", "Reports"],
  },
];

export const FEATURE_SCOPE = {
  Dashboard: "System overview for real scored events, replay dry-run, model artifacts, validation, pipeline evidence, and reports.",
  "Match Browser": "Search and inspect API-backed scored matches from the local replay sample.",
  Players: "Sample-derived player directory from scored local matches, not official ATP profiles.",
  "Player Comparison": "Sample-derived comparison using local scored event appearances and risk exposure.",
  Tournaments: "Planned tournament explorer. Current API does not expose official tournament metadata.",
  "Surface Analytics": "Surface metadata is unavailable in the current sample; this module documents the blocker.",
  Rankings: "Sample-derived ranking from local scored matches, not official ATP rankings.",
  "Replay Center": "Local replay dry-run evidence and selected match point stream. Kafka runtime is not claimed as executed.",
  "Point Timeline": "Chronological point-level scored events for the selected match.",
  "Replay Manifest": "Validated replay artifact summary. A dedicated manifest API endpoint is planned.",
  "Prediction Center": "Point-level scoring center using the published odds model output, not match-winner betting prediction.",
  "Model Performance": "Published odds and risk artifact metadata with real AUC, Brier, benchmark, and validation status where available.",
  "Data Explorer": "Project artifact inventory from validated local outputs and documented counts.",
  Validation: "Final validation status from API, scored events, model, replay, frontend, and preflight reports.",
  "Pipeline Monitor": "Local JSONL scorer throughput, latency, API readiness, and replay dry-run state.",
  Reports: "Submission and audit document index for the final demo.",
};
