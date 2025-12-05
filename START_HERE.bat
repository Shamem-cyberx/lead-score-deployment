@echo off
REM RAKEZ Lead Scoring - Quick Start
echo.
echo ========================================
echo   RAKEZ Lead Scoring Model
echo   Quick Start Launcher
echo ========================================
echo.
echo Please select an option:
echo.
echo 1. Setup (First time only)
echo 2. Start All Services (API + Dashboard)
echo 3. Start API Only
echo 4. Start Dashboard Only
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running setup...
    python setup.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting all services...
    python start.py
) else if "%choice%"=="3" (
    echo.
    echo Starting API only...
    python start.py --api-only
) else if "%choice%"=="4" (
    echo.
    echo Starting Dashboard only...
    python start.py --dashboard-only
) else if "%choice%"=="5" (
    exit
) else (
    echo Invalid choice!
    pause
)

