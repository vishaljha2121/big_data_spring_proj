#!/usr/bin/env python3
"""Contract-only replay manifest existence check for Milestone 2.5."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    parser.add_argument("--schema", type=Path, default=Path("contracts/replay_manifest_schema.json"))
    args = parser.parse_args()
    if not args.manifest.exists():
        raise SystemExit(f"missing replay manifest: {args.manifest}")
    if not args.schema.exists():
        raise SystemExit(f"missing replay manifest schema: {args.schema}")
    print(f"replay manifest contract inputs exist: manifest={args.manifest}, schema={args.schema}")


if __name__ == "__main__":
    main()
