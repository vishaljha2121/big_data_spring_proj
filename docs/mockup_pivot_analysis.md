# Mockup Pivot Analysis

## Mockup Structure Summary

The local mockup reference in `docs/mockup_reference/mockup.html` presents a full product shell rather than a single dashboard. Its core structure is:

- fixed left sidebar navigation
- sticky top header
- feature-scope description banner
- page-specific analytics cards
- reusable metric, table, chart, status, and progress components
- product modules for analytics, replay, model, and data-operations workflows

## Mockup Navigation Groups

- Analytics: Dashboard, Match Browser, Players, Player Comparison, Tournaments, Surface Analytics, Rankings
- Replay: Replay Center, Point Timeline, Replay Manifest
- ML Model: Prediction Center, Model Performance
- Data Ops: Data Explorer, Validation, Pipeline Monitor, Reports

## Mockup Visual Language

The mockup uses a premium tennis analytics style:

- deep green app sidebar
- cream main canvas
- gold accent color
- subtle purple accent for model and confidence highlights
- rounded cards with soft borders
- compact KPI cards and structured tables
- mini line charts and progress bars

The implementation recreates this style in plain CSS to keep the Vite demo stable and avoid adding a risky Tailwind migration this close to submission.

## Current Frontend Gap Analysis

The previous dashboard was polished enough for a single-page demo, but it still felt like a scoring dashboard rather than a product. Gaps addressed in this pivot:

- no durable product navigation
- limited page-level context
- match, replay, model, and validation evidence were concentrated in one long page
- planned modules were not visible as part of the product roadmap
- data operations and report evidence were underemphasized

## Existing Real API Data Mapping

The current FastAPI service provides real local-demo data for:

- service health and readiness
- system summary
- scored event rows
- match summaries and selected match event streams
- risk summary and risk events
- current model metadata
- scoring benchmark metrics

These endpoints remain the only runtime data source for the frontend.

## Pages Real Now

- Dashboard
- Match Browser
- Replay Center
- Point Timeline
- Prediction Center, framed as point-level scoring
- Model Performance
- Data Explorer
- Validation
- Pipeline Monitor
- Reports

## Pages Partial Or Reference-Only

- Players: derived from scored sample matches, not official player profiles
- Player Comparison: derived from scored sample appearances
- Tournaments: planned because official tournament metadata is not exposed by the API
- Surface Analytics: blocked by unavailable surface metadata
- Rankings: sample-derived only, not official ATP rankings
- Replay Manifest: validated artifact exists in the repo, but a dedicated manifest API endpoint is planned

## Implementation Risks

- Do not mix mockup placeholder data with real model metrics.
- Do not present point probabilities as betting odds or match-win probabilities.
- Do not claim official rankings or validated surface analytics.
- Do not claim Kafka runtime execution; the local demo uses JSONL replay/scoring.
- Keep the existing API and one-command demo unchanged.

## Component Migration Plan

- Add `shell/` components for app shell, sidebar, top header, feature-scope banner, and grouped navigation.
- Add generic reusable components: `Card`, `MetricCard`, `DataTable`, `ProgressBar`, `MiniLineChart`, `StatusBadge`, and `EmptyState`.
- Preserve existing domain components where useful, including probability bars, risk badges, and timeline chart behavior.
- Add page modules for the full mockup navigation surface.
- Keep all data wiring in `api/client.js` and derived frontend-only summaries in `utils/derivedMetrics.js`.
- Use planned-module cards whenever the backend does not expose a real endpoint.
