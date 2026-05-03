#!/usr/bin/env python3
"""Milestone 3A Track B stub: replay manifest rows to Kafka."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    parser.add_argument("--topic-config", type=Path, default=Path("infra/kafka/topic_config.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track B owns Kafka replay producer implementation. "
        f"Contract inputs are manifest={args.manifest}, topic_config={args.topic_config}, dry_run={args.dry_run}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
