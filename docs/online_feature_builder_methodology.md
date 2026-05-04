# Online Feature Builder Methodology

## Purpose

The online feature builder converts raw replay point events into the exact feature columns expected by `data/models/odds/v1/feature_schema.json`.

## State Model

State is maintained independently per `synthetic_match_id`. Each match state tracks:

- prior points played
- prior player A/player B point wins
- prior server/receiver point counts and wins
- recent point winners for 5-point and 10-point windows
- prior ace and double-fault counts
- previous replay offset seconds

## Leakage Prevention

For every input event, the scorer calls the builder before updating match state. The current point winner, ace flag, double-fault flag, and elapsed offset are not added to state until after odds/risk scoring completes.

The first event in each synthetic match therefore has zero prior counts.

## Supported Training Features

All `26` published odds model features are produced online:

- prior point counts and win percentages
- server/receiver prior counts and win percentages
- recent 5/10 point win percentages
- prior ace and double-fault counts
- elapsed-time flags and prior elapsed offset
- server/receiver/player validity booleans

## Defaulted Features

`elapsed_seconds_delta_from_prev` is defaulted to `0.0` when there is no prior elapsed offset. This is imputation-compatible with the published sklearn pipeline and is listed in `scoring_run_report.json`.

## Missing Features

No published odds model features are missing from the online builder.

## Limitations

- Runtime features use replay event fields, not curated batch feature rows.
- Surface, ATP bridge, and rally-length primary features remain excluded by the model schema.
- Interleaved matches are supported because state is keyed by `synthetic_match_id`.
