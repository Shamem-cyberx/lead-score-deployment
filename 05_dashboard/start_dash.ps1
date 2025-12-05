# PowerShell script to start Plotly Dash Dashboard
# Usage: .\start_dash.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAKEZ Lead Scoring Dashboard (Plotly Dash)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if dash is installed
try {
    python -c "import dash" 2>&1 | Out-Null
    Write-Host "Dash is installed" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Dash not installed. Installing now..." -ForegroundColor Yellow
    pip install dash plotly pandas
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting dashboard..." -ForegroundColor Yellow
Write-Host "Dashboard will be available at: http://localhost:8050" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the dashboard
python dash_dashboard.py

