# CourtIQ Final Presentation v2 Speaker Notes

## Slide 1: Title

**What to say:** Open by framing CourtIQ as more than a notebook or dashboard: it is a complete local data-to-product system. Say that the project starts from historical point-level tennis data, makes it trustworthy, replays it as events, scores it, and serves it in a polished analytics product. Transition by saying the next slide explains the problem that motivated that architecture.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 2: Problem + Goal

**What to say:** Explain that raw historical point data is not directly usable for a streaming scoring demo. The data has missing fields and score-state subtleties, and a model can easily leak future information if features are computed incorrectly. The goal was to create a reliable and honest end-to-end path: validated data, replay stream, online features, point scoring, risk review signal, API, and dashboard.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 3: Final Product Demo Snapshot

**What to say:** Describe what the audience will see in the demo. The dashboard is backed by real FastAPI responses over validated scored outputs. Point out that the UI has sections for analytics, replay, model evidence, validation, and reports. Transition to why this qualifies as Big Data rather than just a UI demo.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 4: Why This Satisfies Big Data Scope

**What to say:** Use the metric cards first: 1.92 million points, 10.5 thousand matches, almost 1.92 million replay events, and 20 Kafka partitions. Then explain the architectural pieces: Parquet zones, contracts, quality reports, Kafka replay, Spark Structured Streaming, checkpointing, and API serving. Be explicit that the local demo is bounded, but the architecture is horizontally scalable.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 5: Dataset Scale + Data Quality

**What to say:** Talk about the data foundation. Singles point data was curated into Parquet, invalid and special cases were counted and handled, and reports track feature availability. Mention limitations here, not later: surface coverage is unavailable, rally length is sparse, and ATP bridge features are not claimed.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 6: End-to-End Architecture

**What to say:** Walk left to right through the diagram: Parquet data lake, model artifacts, replay stream, Spark scoring, scored output, FastAPI, and dashboard. The important message is that every stage has a validation or contract artifact, so the demo is reproducible.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 7: Data Lake + Cleaning Pipeline

**What to say:** Explain the zones and the safety principle. Raw/staging inputs are not used directly in later stages. Curated singles data feeds features, baselines, replay manifest, and scored outputs. Transition by focusing on the feature layer, where leakage prevention matters most.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 8: Point-in-Time Feature Engineering

**What to say:** Use the diagram to explain event k. The feature row for event k only uses prior points, then the model scores the current point, and only after scoring is the state updated. This is important because including current score/outcome information can inflate metrics. Tests prove the first row counts and rolling windows are correct.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 9: Model Training + Evaluation

**What to say:** Describe the model as an MVP point-outcome model, not a betting or match-win model. The target is Player A wins the current point. Mention feature count, selected model type, AUC, Brier score, and two-phase publication. Explain that schema hashes and fixture scoring protect inference compatibility.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 10: Replay System

**What to say:** Explain that the replay manifest turns historical matches into deterministic event streams with synthetic match and event IDs. Those IDs are replay metadata, not fake match labels. The same canonical event contract supports JSONL fallback and Kafka publishing.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 11: Kafka + Spark Structured Streaming

**What to say:** This is the strongest streaming evidence slide. State clearly: Kafka ran locally, the topic had 20 partitions, the replay producer published 1000 canonical events, Spark Structured Streaming consumed the topic, foreachBatch reused the validated scorer, and the output was checkpointed and validated. Do not overclaim production exactly-once semantics.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 12: Scoring + Risk Pipeline

**What to say:** Explain the runtime scoring sequence: event arrives, online feature builder updates per-match state, odds model predicts point probability, risk config calculates a conservative review signal, then the scored event is written. Say explicitly that risk is not proof of misconduct.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 13: API + Centre Court Dashboard

**What to say:** Use the screenshots. The API exposes summary, matches, scored events, replay catalog, risk, model, and benchmark endpoints. The frontend organizes those into Analytics, Replay, ML Model, and Data Ops. Note that unsupported pages are labeled planned or sample-derived.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 14: Validation Evidence Matrix

**What to say:** Summarize proof rather than implementation. The matrix shows data, model, replay, Kafka, Spark, API, frontend, and tests all with evidence paths. Mention 70 passing tests and PASSED runtime reports. Transition to the problems solved along the way.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 15: Difficulties + Engineering Tradeoffs

**What to say:** Use the Problem Decision Result format. Surface/rally sparsity led to feature exclusions. Leakage risk led to lagged features and tests. Historical data needed deterministic replay IDs. Kafka/Spark friction led to image fixes and foreachBatch. Product polish required careful truthfulness.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 16: Team Contributions

**What to say:** Use this slide to map the work to three team members without inventing names. Member 1 owns data engineering and validation, Member 2 owns features/model/risk/evaluation, and Member 3 owns streaming/API/frontend/demo. Mention shared ownership of tests and documentation.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 17: Limitations + Future Work

**What to say:** Be candid. Point probabilities are not betting odds or match-win probabilities. Risk is not misconduct detection. Surface analytics, official rankings, and ATP bridge are future integrations. The runtime is local, not production. Future work is managed streaming, persistent serving, richer metadata, and monitoring.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.

## Slide 18: Demo Flow + Closing

**What to say:** Close with the concrete demo path. Start the local product with run_full_demo, show dashboard, match browser, replay center, point timeline, model performance, validation, and pipeline monitor. If time permits, show run_streaming_demo for Kafka/Spark proof. End by saying the project demonstrates a validated local Big Data analytics system from raw point data to product UI.

**Transition:** Move to the next slide by connecting the current evidence to the next layer of the system.
