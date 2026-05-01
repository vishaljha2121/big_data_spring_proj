# Skill: Point-in-Time Feature Engineering

Use this skill whenever creating features for the tennis big data project.

## Non-Negotiable Rule

A feature row for event_index = k may only use information from rows with event_index < k in the same match.

The current row's point_winner, server_won outcome, ace flag, double fault flag, or any other current-point outcome must not be included in features ending with `_before`.

## Required Checks

Always test:

- first point in each match has zero prior counts
- row k cumulative features equal aggregation over rows < k
- recent window features use shifted rolling windows
- no future rows influence current features
- labels are separated from features

## Sparse Feature Rules

- rally_length is sparse and must be optional
- surface is unavailable and must not be invented
- elapsed_seconds is partially missing and must have availability flags

## Baseline Rules

- unknown placeholders are invalid/placeholder baselines
- strong baseline requires at least 200 points
- moderate baseline requires at least 50 points
- weak baseline is below 50 points
- do not create surface baselines unless surface is actually present

## Replay Manifest Rules

- deterministic synthetic_match_id
- deterministic synthetic_event_id
- monotonic replay_order within synthetic_match_id
- monotonic replay_offset_seconds within synthetic_match_id
- default interval = 2 seconds when elapsed_seconds is missing
