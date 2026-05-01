# Baseline Generation Audit

## Baseline Logic

Player baselines were computed from curated singles point events. Each player receives match count, point volume, serve/return win rates, ace and double-fault rates, serve-speed averages, rally availability, and elapsed-time availability.

## Sample Thresholds

- `strong`: `total_points >= 200`
- `moderate`: `total_points >= 50`
- `weak`: `total_points < 50`
- `invalid_or_placeholder`: deterministic unknown-player placeholders, regardless of sample size

## Unknown-Player Handling

Unknown placeholders are retained for auditability but are never assigned strong baselines. Placeholder count: 32.

## Surface And Rally Limitations

Surface-specific baselines are blocked because curated surface metadata is unavailable. Rally averages are sparse and should remain secondary until coverage improves.

## Quality Distribution

- Players: 1891
- Strong: 1616
- Moderate: 242
- Weak: 1
- Placeholder: 32
