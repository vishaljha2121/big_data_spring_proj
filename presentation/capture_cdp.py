#!/usr/bin/env python3
"""Capture SPA screenshots using Chrome DevTools Protocol."""
import json
import subprocess
import time
import socket
import urllib.request
import base64
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = Path(__file__).resolve().parent / "assets_v2" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

CDP_PORT = 9333

PAGES = [
    ("dashboard_overview", "http://127.0.0.1:5173/", 6),
    ("match_browser", "http://127.0.0.1:5173/match-browser", 5),
    ("replay_center", "http://127.0.0.1:5173/replay-center", 5),
    ("point_timeline", "http://127.0.0.1:5173/point-timeline", 5),
    ("model_performance", "http://127.0.0.1:5173/model-performance", 5),
    ("validation", "http://127.0.0.1:5173/validation", 5),
    ("pipeline_monitor", "http://127.0.0.1:5173/pipeline-monitor", 5),
    ("prediction_center", "http://127.0.0.1:5173/prediction-center", 5),
]


def cdp_request(ws_url, method, params=None, timeout=15):
    """Send CDP command via HTTP endpoint."""
    import websocket  # pip install websocket-client
    ws = websocket.create_connection(ws_url, timeout=timeout)
    msg = {"id": 1, "method": method, "params": params or {}}
    ws.send(json.dumps(msg))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == 1:
            ws.close()
            return resp.get("result", {})


def main():
    # Check if websocket-client is available
    try:
        import websocket
    except ImportError:
        print("Installing websocket-client...")
        subprocess.run([".venv/bin/pip", "install", "websocket-client"], 
                      capture_output=True, cwd=str(Path(__file__).resolve().parents[1]))
        import websocket

    # Start Chrome with debugging port
    chrome_proc = subprocess.Popen([
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        "--window-size=1440,900",
        "--hide-scrollbars",
        "--force-device-scale-factor=2",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    try:
        # Get the debugger targets
        resp = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list")
        targets = json.loads(resp.read())
        
        if not targets:
            print("No targets found")
            return
        
        ws_url = targets[0]["webSocketDebuggerUrl"]
        print(f"Connected to Chrome CDP: {ws_url}")
        
        for name, url, wait_sec in PAGES:
            print(f"Capturing {name} ...")
            try:
                import websocket as ws_mod
                ws = ws_mod.create_connection(ws_url, timeout=20)
                
                # Navigate
                msg_id = 1
                ws.send(json.dumps({"id": msg_id, "method": "Page.navigate", "params": {"url": url}}))
                # Wait for response
                while True:
                    r = json.loads(ws.recv())
                    if r.get("id") == msg_id:
                        break
                
                # Wait for content to load
                time.sleep(wait_sec)
                
                # Take screenshot
                msg_id = 2
                ws.send(json.dumps({"id": msg_id, "method": "Page.captureScreenshot", "params": {
                    "format": "png",
                    "clip": {"x": 0, "y": 0, "width": 1440, "height": 900, "scale": 2}
                }}))
                while True:
                    r = json.loads(ws.recv())
                    if r.get("id") == msg_id:
                        data = r.get("result", {}).get("data", "")
                        if data:
                            out_path = OUT / f"{name}.png"
                            out_path.write_bytes(base64.b64decode(data))
                            print(f"  OK {name}: {out_path.stat().st_size} bytes")
                        else:
                            print(f"  FAIL {name}: no data")
                        break
                
                ws.close()
            except Exception as e:
                print(f"  ERR {name}: {e}")
    
    finally:
        chrome_proc.terminate()
        chrome_proc.wait()
        print("Chrome terminated.")


if __name__ == "__main__":
    main()
