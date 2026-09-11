#!/usr/bin/env python3
import argparse
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(ROOT_DIR, "build")

app = FastAPI()
app.mount("/", StaticFiles(directory=BUILD_DIR, html=True), name="prayers")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Jainism prayers server.")
    parser.add_argument("--port", type=int, default=8007, help="Port to run the server on.")
    args = parser.parse_args()

    if not os.path.isdir(BUILD_DIR):
        raise SystemExit(f"Error: '{BUILD_DIR}' does not exist. Run ./build.sh first.")

    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info", proxy_headers=True)
