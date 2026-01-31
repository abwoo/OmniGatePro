# Artfish Entry Script (Windows PowerShell)
# Handles dependency checks and launches the Python CLI

$ErrorActionPreference = "Stop"

Write-Host "Starting Artfish Runtime Engine..." -ForegroundColor Cyan

# 1. Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# 2. Check Dependencies (Silent check)
$depsCheck = python -c "import rich, typer, questionary" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependencies missing. Installing from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# 3. Launch CLI
$env:PYTHONPATH = ".;$env:PYTHONPATH"
python cli.py @args
