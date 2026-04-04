#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="$(command -v python3.11 || command -v python3.10 || command -v python3)"

if [ -x ".venv/bin/python" ]; then
  VENV_VERSION="$(.venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  TARGET_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  if [ "$VENV_VERSION" != "$TARGET_VERSION" ]; then
    rm -rf .venv
  fi
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r backend/requirements.txt

cd frontend
npm install
cd "$ROOT_DIR"

trap 'kill $(jobs -p) >/dev/null 2>&1 || true' EXIT

source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
(
  cd frontend
  npm run dev -- --host 0.0.0.0 --port 5173
) &

sleep 5
open http://localhost:5173
wait
