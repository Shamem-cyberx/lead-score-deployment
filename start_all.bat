@echo off
REM ============================================================
REM RAKEZ Lead Scoring - Start All Services
REM ============================================================
echo.
echo ============================================================
echo   RAKEZ Lead Scoring - Starting All Services
echo ============================================================
echo.

REM Find Python - try multiple methods
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Method 1: Try python command first (most reliable)
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python -c "import sys" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
        set PYTHON_FOUND=1
        goto :found_python
    )
)

REM Method 2: Try py launcher (but verify it actually works)
REM Test if py can actually run Python, not just if it exists
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -c "import sys; print(sys.version)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
        set PYTHON_FOUND=1
        goto :found_python
    )
)

REM Method 2: Try common Python paths
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :found_python
)
if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    goto :found_python
)
if exist "C:\Python310\python.exe" (
    set PYTHON_CMD=C:\Python310\python.exe
    goto :found_python
)

REM Method 3: Try AppData
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
        set PYTHON_FOUND=1
        goto :found_python
    )
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
        set PYTHON_FOUND=1
        goto :found_python
    )
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
        set PYTHON_FOUND=1
        goto :found_python
    )
)

REM If not found, show error
if %PYTHON_FOUND% EQU 0 (
    echo.
    echo ============================================================
    echo   [ERROR] Python not found or not working!
    echo ============================================================
    echo.
    echo Your 'py' launcher exists but points to a missing Python310.
    echo Python is not installed or not in your PATH.
    echo.
    echo SOLUTION: Install Python
    echo.
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. Run the installer
    echo 3. IMPORTANT: Check "Add Python to PATH" during installation
    echo 4. Close and reopen this terminal after installation
    echo 5. Run this script again: .\start_all.bat
    echo.
    echo See INSTALL_PYTHON.md for detailed instructions
    echo.
    pause
    exit /b 1
)

:found_python
echo [OK] Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if in project root
if not exist "03_api\fastapi_app.py" (
    echo [ERROR] Please run from project root directory
    pause
    exit /b 1
)

echo ============================================================
echo [1/2] Starting Backend (FastAPI)...
echo ============================================================

REM Check backend dependencies
%PYTHON_CMD% -c "import fastapi, uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing backend dependencies...
    %PYTHON_CMD% -m pip install fastapi uvicorn mlflow pandas numpy scikit-learn
)

REM Start backend in new window
start "RAKEZ Backend API" cmd /k "cd /d %~dp0\03_api && %PYTHON_CMD% -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000"

echo [OK] Backend starting in new window
echo      URL: http://127.0.0.1:8000
echo.

timeout /t 3 /nobreak >nul

echo ============================================================
echo [2/2] Starting Frontend (Dashboard)...
echo ============================================================

REM Check frontend dependencies
%PYTHON_CMD% -c "import dash, plotly, pandas" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing frontend dependencies...
    %PYTHON_CMD% -m pip install dash plotly pandas dash-bootstrap-components
)

REM Start frontend
cd /d "%~dp0\05_dashboard"

echo [OK] Dashboard starting...
echo      URL: http://localhost:8050
echo.
echo ============================================================
echo   Services Started!
echo ============================================================
echo   Backend:  http://127.0.0.1:8000
echo   Dashboard: http://localhost:8050
echo.
echo   Press Ctrl+C to stop dashboard
echo   (Backend runs in separate window)
echo ============================================================
echo.

%PYTHON_CMD% dash_dashboard.py

pause

