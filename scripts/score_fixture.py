#!/usr/bin/env python3
"""Milestone 2B Track A stub: score published validation fixtures."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--model-type", choices=["odds", "risk"], required=True)
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()
    print(
        "NOT IMPLEMENTED: Track A must implement fixture scoring after real artifacts exist. "
        f"Requested model_type={args.model_type}, version={args.version}, models={args.models}."
    )
    raise SystemExit(2)


if __name__ == "__main__":
    main()
