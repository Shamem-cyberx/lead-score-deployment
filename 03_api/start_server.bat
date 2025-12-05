@echo off
echo ============================================================
echo Starting FastAPI Server for Explainability Testing
echo ============================================================
echo.
echo Server will start on: http://127.0.0.1:8000
echo.
echo Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

cd /d "%~dp0"
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000

pause

