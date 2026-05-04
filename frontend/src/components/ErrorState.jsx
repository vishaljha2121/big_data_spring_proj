import React from "react";

export default function ErrorState({ error }) {
  return (
    <section className="state-panel error">
      <h2>API unavailable</h2>
      <p>The file-backed FastAPI service is not reachable. Start it with:</p>
      <code>.venv/bin/python scripts/run_api.py --host 127.0.0.1 --port 8000</code>
      <p className="muted">{error && error.message ? error.message : String(error)}</p>
    </section>
  );
}
