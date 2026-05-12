#!/usr/bin/env python3
"""Capture SPA screenshots by clicking sidebar links via Selenium."""
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUT = Path(__file__).resolve().parent / "assets_v2" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

# Link text in sidebar -> screenshot name
PAGES = [
    ("Dashboard", "dashboard_overview", 6),
    ("Match Browser", "match_browser", 5),
    ("Replay Center", "replay_center", 5),
    ("Point Timeline", "point_timeline", 5),
    ("Model Performance", "model_performance", 5),
    ("Prediction Center", "prediction_center", 5),
    ("Validation", "validation", 5),
    ("Pipeline Monitor", "pipeline_monitor", 5),
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
    
    # Start with the dashboard page
    print("Loading SPA at http://127.0.0.1:5173/ ...")
    driver.get("http://127.0.0.1:5173/")
    time.sleep(8)  # Wait for initial load
    
    for link_text, name, wait in PAGES:
        print(f"Navigating to {link_text} ...")
        try:
            # Find and click the sidebar link
            links = driver.find_elements(By.LINK_TEXT, link_text)
            if not links:
                # Try partial match
                links = driver.find_elements(By.PARTIAL_LINK_TEXT, link_text)
            if not links:
                # Try xpath
                links = driver.find_elements(By.XPATH, f"//a[contains(text(), '{link_text}')]")
            
            if links:
                links[0].click()
                time.sleep(wait)
                out_path = str(OUT / f"{name}.png")
                driver.save_screenshot(out_path)
                size = Path(out_path).stat().st_size
                print(f"  OK {name}: {size} bytes")
                results[name] = "OK"
            else:
                print(f"  SKIP {name}: link '{link_text}' not found")
                results[name] = "SKIP"
        except Exception as e:
            print(f"  ERR {name}: {e}")
            results[name] = "FAILED"
    
    # Also capture FastAPI docs
    print("Capturing FastAPI docs ...")
    try:
        driver.get("http://127.0.0.1:8000/docs")
        time.sleep(4)
        driver.save_screenshot(str(OUT / "fastapi_docs.png"))
        print(f"  OK fastapi_docs")
        results["fastapi_docs"] = "OK"
    except Exception as e:
        print(f"  ERR fastapi_docs: {e}")
        results["fastapi_docs"] = "FAILED"
    
    driver.quit()
    
    (OUT / "capture_results.json").write_text(json.dumps(results, indent=2))
    print("\n--- Results ---")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
