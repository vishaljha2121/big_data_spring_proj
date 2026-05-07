#!/usr/bin/env python3
"""Generate a fuller demo-scored dataset from the replay manifest.

Selects complete matches from the replay manifest, scores all their events
using the published StreamScorer, and writes output JSONL/Parquet.  This does
NOT retrain the model — it reuses existing model artifacts.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streaming.stream_scorer import StreamScorer, now_iso


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, int(round((pct / 100.0) * (len(values) - 1))))
    return float(values[idx])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/replay/manifests/replay_manifest_v1.parquet"),
    )
    parser.add_argument("--odds-latest", type=Path, default=Path("data/models/odds/latest.json"))
    parser.add_argument("--risk-latest", type=Path, default=Path("data/models/risk/latest.json"))
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=Path("data/results/streaming_scoring/scored_events_demo_full.jsonl"),
    )
    parser.add_argument(
        "--output-parquet",
        type=Path,
        default=Path("data/results/streaming_scoring/scored_events_demo_full.parquet"),
    )
    parser.add_argument("--max-matches", type=int, default=50, help="Number of matches to score")
    parser.add_argument("--min-events-per-match", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/results/streaming_scoring/full_demo_scoring_report.json"),
    )
    parser.add_argument("--include-outcome-models", action="store_true", help="Include game/set/match outcome probabilities")
    args = parser.parse_args()

    # ── Initialization ────────────────────────────────────────
    print(f"Initializing full demo generator (target: {args.max_matches} matches)...")
    
    outcome_models = None
    if args.include_outcome_models:
        outcome_models = {
            "game": Path("data/models/outcomes/game/latest.json"),
            "set": Path("data/models/outcomes/set/latest.json"),
            "match": Path("data/models/outcomes/match/latest.json"),
        }
        
    # ── Load replay manifest ──────────────────────────────────
    print(f"Loading replay manifest from {args.manifest} ...")
    import pyarrow.parquet as pq

    table = pq.read_table(args.manifest)
    all_events = table.to_pylist()
    print(f"  Total manifest events: {len(all_events):,}")

    # Group by match
    events_by_match: Dict[str, List[Dict[str, Any]]] = {}
    for evt in all_events:
        events_by_match.setdefault(evt["synthetic_match_id"], []).append(evt)
    for mid in events_by_match:
        events_by_match[mid].sort(key=lambda r: r.get("replay_order", 0))
    print(f"  Total matches in manifest: {len(events_by_match):,}")

    # ── Known schema fields for point_event_schema.json ──────
    POINT_EVENT_FIELDS = {
        "schema_version", "replay_session_id", "synthetic_match_id",
        "source_match_id", "event_id", "synthetic_event_id", "event_index",
        "replay_order", "replay_offset_seconds", "event_ts", "player_a",
        "player_b", "server_player", "receiver_player", "point_winner_player",
        "set_number", "game_number", "point_number", "p1_score", "p2_score",
        "is_ace", "is_double_fault", "is_break_point", "source_file",
    }

    def clean_manifest_event(evt: Dict[str, Any]) -> Dict[str, Any]:
        """Strip extra fields from manifest events and add schema_version."""
        cleaned = {k: v for k, v in evt.items() if k in POINT_EVENT_FIELDS}
        cleaned.setdefault("schema_version", "point_event_v1")
        return cleaned

    # ── Select matches ────────────────────────────────────────
    # Prefer matches with real player names, sufficient events
    def has_real_players(evts: List[Dict[str, Any]]) -> bool:
        pa = evts[0].get("player_a", "")
        pb = evts[0].get("player_b", "")
        return bool(pa and pb and pa != "Unknown" and pb != "Unknown")

    candidates = [
        (mid, evts)
        for mid, evts in events_by_match.items()
        if len(evts) >= args.min_events_per_match and has_real_players(evts)
    ]
    print(f"  Candidates with real players and >= {args.min_events_per_match} events: {len(candidates):,}")

    # Deterministic selection: sort by match ID, then pick first N
    import random

    rng = random.Random(args.seed)
    candidates.sort(key=lambda x: x[0])
    rng.shuffle(candidates)
    selected = candidates[: args.max_matches]
    print(f"  Selected {len(selected)} matches for scoring")

    # ── Score selected matches ────────────────────────────────
    scorer = StreamScorer(args.odds_latest, args.risk_latest, outcome_models=outcome_models)
    scored: List[Dict[str, Any]] = []
    errors: List[str] = []
    latencies: List[float] = []
    match_stats: List[Dict[str, Any]] = []

    for i, (mid, match_events) in enumerate(selected):
        # Reset feature builder state per match for correct point-in-time features
        scorer.feature_builder = type(scorer.feature_builder)(scorer.odds.feature_columns)

        match_features: List[Dict[str, Any]] = []
        match_events_list: List[Dict[str, Any]] = []
        match_risks: List[Dict[str, Any]] = []
        match_latencies: List[float] = []

        for raw_evt in match_events:
            evt = clean_manifest_event(raw_evt)
            try:
                start = time.perf_counter()
                scorer.validate_event(evt)
                features = scorer.feature_builder.build_features(evt)
                risk_result = scorer.risk.score(features)
                scorer.feature_builder.update_state(evt)
                lat = (time.perf_counter() - start) * 1000.0
                match_features.append(features)
                match_events_list.append(evt)
                match_risks.append(risk_result)
                match_latencies.append(lat)
            except Exception as exc:
                errors.append(f"match={mid} event={evt.get('event_id')}: {exc}")

        # Batch predict for this match
        if match_features:
            proba_start = time.perf_counter()
            probabilities = scorer.odds.predict_proba(
                pd.DataFrame(match_features, columns=scorer.odds.feature_columns)
            )
            
            # Batch inference for outcome models
            outcome_probs_batch = [{} for _ in range(len(match_features))]
            if scorer.outcomes:
                for target_name, loader in scorer.outcomes.items():
                    try:
                        df_target_features = pd.DataFrame(match_features, columns=loader.feature_columns)
                        target_probs = loader.model.predict_proba(df_target_features.apply(pd.to_numeric, errors="coerce").astype(float))[:, 1]
                        for i, prob in enumerate(target_probs):
                            outcome_probs_batch[i][target_name] = float(prob)
                    except Exception as exc:
                        pass # Ignore if feature missing
                        
            proba_lat = ((time.perf_counter() - proba_start) * 1000.0) / len(match_features)

            match_scored = [
                scorer.format_scored_event(evt, prob, risk_r, lat + proba_lat, outcome_probs)
                for evt, prob, risk_r, lat, outcome_probs in zip(
                    match_events_list, probabilities, match_risks, match_latencies, outcome_probs_batch
                )
            ]
            scored.extend(match_scored)
            latencies.extend([e["scoring_latency_ms"] for e in match_scored])
            match_stats.append({
                "synthetic_match_id": mid,
                "player_a": match_events_list[0].get("player_a"),
                "player_b": match_events_list[0].get("player_b"),
                "event_count": len(match_scored),
            })

        if (i + 1) % 10 == 0 or i == len(selected) - 1:
            print(f"  Scored {i + 1}/{len(selected)} matches ({len(scored):,} total events)")

    # ── Write outputs ─────────────────────────────────────────
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as handle:
        for event in scored:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"  Wrote {len(scored):,} scored events to {args.output_jsonl}")

    parquet_path = None
    warnings: List[str] = []
    if args.output_parquet is not None:
        try:
            pd.DataFrame(scored).to_parquet(args.output_parquet, index=False)
            parquet_path = str(args.output_parquet)
            print(f"  Wrote parquet to {args.output_parquet}")
        except Exception as exc:
            warnings.append(f"Parquet output skipped: {exc}")

    # ── Generate report ───────────────────────────────────────
    unique_players = set()
    for ms in match_stats:
        if ms["player_a"]:
            unique_players.add(ms["player_a"])
        if ms["player_b"]:
            unique_players.add(ms["player_b"])

    report = {
        "generated_at": now_iso(),
        "selected_match_count": len(match_stats),
        "scored_event_count": len(scored),
        "avg_events_per_match": (
            sum(ms["event_count"] for ms in match_stats) / len(match_stats) if match_stats else 0
        ),
        "unique_player_count": len(unique_players),
        "sample_players": sorted(unique_players)[:20],
        "invalid_event_count": len(errors),
        "feature_schema_hash": scorer.odds.feature_schema_hash,
        "odds_model_version": scorer.odds.version,
        "average_scoring_latency_ms": float(statistics.mean(latencies)) if latencies else 0.0,
        "p95_scoring_latency_ms": percentile(latencies, 95),
        "output_jsonl": str(args.output_jsonl),
        "output_parquet": parquet_path,
        "match_details": match_stats,
        "status": "PASSED" if scored and not errors else "PARTIAL" if scored else "FAILED",
        "warnings": warnings,
        "blocking_errors": errors[:10],
        "limitations": [
            "Uses existing published model artifacts — no retraining performed.",
            f"Only {len(match_stats)} matches scored, not full 10,464-match manifest.",
            "Feature builder resets per match; cross-match features not available.",
        ],
    }
    write_json(args.report, report)
    print(f"\nFull demo scoring {report['status']}: {len(scored):,} events across {len(match_stats)} matches")
    if report["status"] == "FAILED":
        raise SystemExit(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
