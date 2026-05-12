#!/usr/bin/env python3
"""Capture SPA screenshots using Selenium + headless Chrome."""
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

OUT = Path(__file__).resolve().parent / "assets_v2" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("dashboard_overview", "http://127.0.0.1:5173/", 8),
    ("match_browser", "http://127.0.0.1:5173/match-browser", 5),
    ("replay_center", "http://127.0.0.1:5173/replay-center", 5),
    ("point_timeline", "http://127.0.0.1:5173/point-timeline", 5),
    ("model_performance", "http://127.0.0.1:5173/model-performance", 5),
    ("validation", "http://127.0.0.1:5173/validation", 5),
    ("pipeline_monitor", "http://127.0.0.1:5173/pipeline-monitor", 5),
    ("prediction_center", "http://127.0.0.1:5173/prediction-center", 5),
    ("fastapi_docs", "http://127.0.0.1:8000/docs", 4),
]


def main():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--force-device-scale-factor=2")
    opts.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    driver = webdriver.Chrome(options=opts)
    results = {}
    
    for name, url, wait in PAGES:
        print(f"Capturing {name} ...")
        try:
            driver.get(url)
            time.sleep(wait)
            out_path = str(OUT / f"{name}.png")
            driver.save_screenshot(out_path)
            size = Path(out_path).stat().st_size
            print(f"  OK {name}: {size} bytes")
            results[name] = "OK"
        except Exception as e:
            print(f"  ERR {name}: {e}")
            results[name] = "FAILED"
    
    driver.quit()
    
    (OUT / "capture_results.json").write_text(json.dumps(results, indent=2))
    print("\n--- Results ---")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
