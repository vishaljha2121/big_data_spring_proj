import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_order_and_offsets_are_monotonic_by_match():
    orders = defaultdict(list)
    offsets = defaultdict(list)
    for line in (ROOT / "data/results/replay_dry_run/sample_events.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        orders[event["synthetic_match_id"]].append(event["replay_order"])
        offsets[event["synthetic_match_id"]].append(event["replay_offset_seconds"])
    for values in orders.values():
        assert values == sorted(values)
    for values in offsets.values():
        assert values == sorted(values)
