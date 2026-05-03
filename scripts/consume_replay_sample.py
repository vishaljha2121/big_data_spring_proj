#!/usr/bin/env python3
"""Milestone 3A Track B stub: consume a small Kafka replay sample."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track B owns Kafka sample consumer implementation. "
        f"Requested topic={args.topic}, limit={args.limit}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
