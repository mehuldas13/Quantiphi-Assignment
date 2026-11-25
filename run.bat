@echo off
REM One-command start for Windows: creates a virtualenv, installs, runs.
cd /d %~dp0
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 'Python 3.10 or newer is required')" || goto :eof
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt
echo.
echo   Open http://127.0.0.1:8000 in your browser (Ctrl+C to stop)
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
