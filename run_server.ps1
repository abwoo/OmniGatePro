Write-Host "Starting Artfish Runtime Engine..." -ForegroundColor Cyan
Write-Host "Checking environment..."

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "venv")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "Starting API Server..." -ForegroundColor Green
Write-Host "The API will be available at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray

# Start Uvicorn
uvicorn api.main:app --reload
