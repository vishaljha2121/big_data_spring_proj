#!/usr/bin/env python3
"""Replay producer configuration helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_topic_config(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
