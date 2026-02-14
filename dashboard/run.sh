#!/bin/bash
# Hotel Intel Dashboard — Quick Start
cd "$(dirname "$0")/.."

# Use existing venv or create one
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q fastapi uvicorn python-dotenv
fi

echo "🏨 Starting Hotel Intel Dashboard on http://localhost:8000"
.venv/bin/python dashboard/server.py
