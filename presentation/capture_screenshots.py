#!/usr/bin/env python3
"""Capture dashboard screenshots using headless Chrome via CDP."""

import subprocess
import time
import json
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent / "assets_v2" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("dashboard_overview", "http://127.0.0.1:5173/", 4),
    ("match_browser", "http://127.0.0.1:5173/match-browser", 4),
    ("replay_center", "http://127.0.0.1:5173/replay-center", 4),
    ("point_timeline", "http://127.0.0.1:5173/point-timeline", 4),
    ("model_performance", "http://127.0.0.1:5173/model-performance", 4),
    ("validation", "http://127.0.0.1:5173/validation", 4),
    ("pipeline_monitor", "http://127.0.0.1:5173/pipeline-monitor", 4),
    ("prediction_center", "http://127.0.0.1:5173/prediction-center", 4),
    ("fastapi_docs", "http://127.0.0.1:8000/docs", 4),
]


def capture(name: str, url: str, wait: int):
    out_path = OUT / f"{name}.png"
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-software-rasterizer",
        f"--screenshot={out_path}",
        f"--window-size=1440,900",
        "--hide-scrollbars",
        "--force-device-scale-factor=2",
        url,
    ]
    try:
        subprocess.run(cmd, timeout=15, capture_output=True)
        time.sleep(0.5)
        if out_path.exists() and out_path.stat().st_size > 5000:
            print(f"  OK  {name}: {out_path.stat().st_size} bytes")
            return True
        else:
            print(f"  FAIL {name}: file missing or too small")
            return False
    except Exception as e:
        print(f"  ERR  {name}: {e}")
        return False


def main():
    results = {}
    for name, url, wait in PAGES:
        print(f"Capturing {name} ...")
        ok = capture(name, url, wait)
        results[name] = "OK" if ok else "FAILED"
    print("\n--- Results ---")
    for k, v in results.items():
        print(f"  {k}: {v}")
    (OUT / "capture_results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
