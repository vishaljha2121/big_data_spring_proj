# Skill: Data Layer Quality and Curated Dataset Construction

Use this skill whenever working on the tennis big data project's raw, cleaned, curated, feature, or replay-preparation datasets.

## Mission

Produce deterministic, validated, project-compliant data layers. Never treat partially cleaned CSV files as final outputs unless they pass the project data contract.

## Core Rules

1. Raw/staging data is not final cleaned data.
2. Final cleaned and curated outputs must be reproducible.
3. Every transformation must produce validation evidence.
4. Every major output must have a data-quality report.
5. Do not silently cast dirty values.
6. Do not silently drop rows without reporting counts.
7. Do not invent labels for anomaly detection.
8. Do not proceed to modeling until the curated layer passes validation.
9. Prefer Parquet for final analytical outputs.
10. Preserve lineage from source file to output row.

## Required Output Artifacts

For any cleaned or curated dataset task, produce:

- Parquet output dataset
- schema JSON
- data_quality_report.json
- feature_availability_report.json where relevant
- human-readable audit markdown
- validation tests

## Canonical Checks

Always check:

- row counts
- file counts
- duplicate IDs
- missing IDs
- schema consistency
- invalid enum values
- null rates
- join coverage
- type normalization
- deterministic ordering
- excluded row counts
- quarantined row counts

## Tennis Project Specific Rules

For MVP:

- Use singles matches only.
- Exclude doubles and mixed matches from curated singles outputs.
- Treat `PointWinner` and `PointServer` values as coded fields that require normalization.
- Do not silently cast values like `1.0`, `2.0`, `0`, `0.0`, blank, or non-numeric strings.
- Treat special `PointNumber` values like `0X`, `0Y`, `45D` as special cases.
- Do not rely on rally length as a primary MVP feature if coverage is sparse.
- event_ts may be null in static curated data; replay generation can create timestamps later.
- event_index must be deterministic within match_id.

## Definition of Done

A data layer task is done only when:

- outputs exist in the expected folder
- schema validation passes
- tests pass
- data quality report exists
- feature availability report exists, if relevant
- human-readable audit exists
- remaining limitations are documented