@echo off
REM ============================================================
REM RAKEZ Lead Scoring - Start Dashboard
REM ============================================================
echo.
echo ============================================================
echo   Starting Dashboard (Plotly Dash)
echo ============================================================
echo.

cd /d "%~dp0\05_dashboard"

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
    echo 4. Close and reopen terminal after installation
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

:found_python
echo [OK] Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check dependencies
echo [1/2] Checking dependencies...
%PYTHON_CMD% -c "import dash, plotly, pandas" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies...
    %PYTHON_CMD% -m pip install dash plotly pandas dash-bootstrap-components
)

echo [2/2] Starting Dashboard...
echo.
echo ============================================================
echo   Dashboard
echo ============================================================
echo   URL: http://localhost:8050
echo   Alternative: http://127.0.0.1:8050
echo.
echo   Press Ctrl+C to stop
echo ============================================================
echo.

%PYTHON_CMD% dash_dashboard.py

pause

