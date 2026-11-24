#!/usr/bin/env bash
# One-command start for macOS / Linux: creates a virtualenv, installs, runs.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
echo "Open http://localhost:8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
