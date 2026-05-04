#!/usr/bin/env python3
"""Run the local FastAPI serving layer."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    uvicorn.run("api.app.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
