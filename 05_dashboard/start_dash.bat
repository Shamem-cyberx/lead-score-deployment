@echo off
REM Start Plotly Dash Dashboard (Fast, Modern UI)
echo ========================================
echo RAKEZ Lead Scoring Dashboard (Plotly Dash)
echo ========================================
echo.
echo Starting dashboard...
echo.
echo IMPORTANT: Use one of these URLs in your browser:
echo   - http://localhost:8050
echo   - http://127.0.0.1:8050
echo.
echo DO NOT use: http://0.0.0.0:8050 (this will NOT work!)
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if dash is installed
python -c "import dash" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Dash not installed. Installing now...
    pip install dash plotly pandas
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Start the dashboard
python dash_dashboard.py

pause

