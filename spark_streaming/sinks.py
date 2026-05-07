"""Local sink helpers for Spark streaming scored output."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd


def append_jsonl(path: Path, rows: Iterable[Dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            count += 1
    return count


def write_parquet_batch(path: Path, rows: List[Dict], batch_id: int) -> Path | None:
    if not rows:
        return None
    path.mkdir(parents=True, exist_ok=True)
    batch_path = path / f"batch-{int(batch_id):06d}.parquet"
    pd.DataFrame(rows).to_parquet(batch_path, index=False)
    return batch_path

