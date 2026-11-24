@echo off
REM One-command start for Windows: creates a virtualenv, installs, runs.
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt
echo Open http://localhost:8000
uvicorn app.main:app --host 0.0.0.0 --port 8000
