# CourtIQ Final Presentation Speaker Notes

## Slide 1: Title slide

Introduce CourtIQ as a validated tennis point-level analytics platform. Emphasize that the project covers data engineering, model artifacts, streaming, API, and product UI.

## Slide 2: Problem statement

Explain that tennis point data is high-volume and messy, and naive models can leak future information. The goal was a reliable end-to-end demo with truthful probability and risk language.

## Slide 3: Product demo overview

Walk through the Centre Court Analytics product: dashboard, match browser, replay center, point scoring, validation, and reports.

## Slide 4: Why this is a Big Data project

Call out 1.9M+ point rows, 10K+ matches, Parquet zones, contracts, Spark-style batch processing, Kafka replay, Spark Structured Streaming, and bounded local scale.

## Slide 5: Dataset and scale

Use the numbers as evidence: curated rows, matches, replay manifest size, and limitations around surface/rally/ATP metadata.

## Slide 6: End-to-end architecture

Trace the full path from curated data lake through features, models, replay, streaming, scored outputs, API, and frontend.

## Slide 7: Data lake + cleaning pipeline

Describe the data lake zones and cleaning decisions: singles filtering, placeholders, quarantine, reports, and schema contracts.

## Slide 8: Feature engineering and point-in-time safety

Emphasize no future leakage: sort by match/event, use lagged cumulative counts, first point zero prior counts, tests prove safety.

## Slide 9: Model training and evaluation

Explain the published model, feature count, AUC/Brier, two-phase publication, and why point-level target is not match prediction.

## Slide 10: Replay architecture

Explain deterministic replay manifest, JSONL fallback, Kafka publishing mode, and canonical event schema.

## Slide 11: Kafka + Spark Structured Streaming architecture

This is the core Big Data evidence slide. Say Kafka and Spark were actually executed locally with 1000 events and checkpointed scored output.

## Slide 12: Scoring + risk pipeline

Explain online feature state, odds scoring, risk config, and careful language: risk is review signal only.

## Slide 13: API and frontend product

Explain FastAPI endpoints, OpenAPI snapshot, response examples, and Centre Court product shell. Mention planned/sample-derived pages are labeled.

## Slide 14: Validation and testing evidence

Summarize 70 passing tests and PASSED reports for API, frontend, Kafka, Spark, model, replay, and final preflight.

## Slide 15: Difficulties and engineering tradeoffs

Discuss data limitations, leakage prevention, Kafka image/runtime hardening, foreachBatch tradeoff, and UI truthfulness.

## Slide 16: Team contributions

Use the three-member split. Replace placeholders with names if needed before presentation.

## Slide 17: Limitations

Be explicit: no betting odds, no misconduct proof, no official rankings, bounded local runtime, no production deployment.

## Slide 18: Future work

Prioritize metadata enrichment, match-level prediction, managed streaming, persistent serving storage, and monitoring.

## Slide 19: Demo flow

Give the exact path to demo: run_full_demo, then pages to show, then optional run_streaming_demo for streaming proof.

## Slide 20: Closing slide

Close with the main accomplishment: validated local Big Data analytics pipeline with streaming evidence and product UI.
