#!/usr/bin/env python3
"""Milestone 2B Track A stub: train the MVP odds model."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--results", type=Path, default=Path("data/results/model_eval"))
    parser.add_argument("--target", default="label_point_winner_is_player_a")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track A owns odds model training. "
        f"Inputs are features={args.features}, models={args.models}, results={args.results}, target={args.target}, seed={args.seed}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
