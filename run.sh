#!/usr/bin/env bash
# One-command start for macOS / Linux: creates a virtualenv, installs, runs.
set -e
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
$PY -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Python 3.10 or newer is required (found %s)" % sys.version.split()[0])'
[ -d .venv ] || $PY -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
echo
echo "  Open http://127.0.0.1:8000 in your browser (Ctrl+C to stop)"
echo
exec python -m uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8000}"
