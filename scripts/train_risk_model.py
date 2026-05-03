#!/usr/bin/env python3
"""Milestone 2B Track A stub: create conservative risk scoring config."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--baselines", type=Path, default=Path("data/baselines"))
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--results", type=Path, default=Path("data/results/model_eval"))
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track A owns risk config creation. "
        f"Inputs are features={args.features}, baselines={args.baselines}, models={args.models}, results={args.results}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
