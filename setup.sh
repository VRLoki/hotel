#!/bin/bash
# ──────────────────────────────────────────────
# Hotel Intel — Project Setup
# Safe to run multiple times (idempotent).
# ──────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

echo "🏨 Hotel Intel — Setup"
echo "─────────────────────────────────"

# 1. Python venv
if [ ! -d ".venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv .venv
else
  echo "✅ Virtual environment exists"
fi

# 2. Dependencies
echo "📦 Installing dependencies..."
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q \
  fastapi \
  uvicorn \
  python-dotenv \
  requests

# 3. .env file
if [ ! -f "app/.env" ]; then
  if [ -f "app/.env.example" ]; then
    cp app/.env.example app/.env
    echo "📝 Created app/.env from .env.example — edit it with your API keys"
  else
    echo "⚠️  No .env.example found, skipping .env creation"
  fi
else
  echo "✅ app/.env already exists"
fi

# 4. Ensure profiles directory exists
mkdir -p app/profiles

echo "─────────────────────────────────"
echo "✅ Setup complete. Run ./dashboard/run.sh to start."
