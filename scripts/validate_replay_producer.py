#!/usr/bin/env python3
"""Milestone 3A Track B stub: validate replay producer contract compliance."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    parser.add_argument("--topic-config", type=Path, default=Path("infra/kafka/topic_config.json"))
    parser.add_argument("--event-schema", type=Path, default=Path("contracts/point_event_schema.json"))
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track B must implement replay producer validation after producer exists. "
        f"Inputs are manifest={args.manifest}, topic_config={args.topic_config}, event_schema={args.event_schema}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
