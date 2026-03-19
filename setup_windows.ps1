# FreeAgentDev Windows One-Click Setup
$ErrorActionPreference = "Stop"
$currentDir = Get-Location

Write-Host " Starting FreeAgentDev Setup..." -ForegroundColor Cyan

# 1. Create Virtual Environment
if (!(Test-Path ".venv")) {
    Write-Host " Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# 2. Install Dependencies
Write-Host " Installing dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

# 3. Initialize Config
Write-Host " Initializing configuration..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" freeagent.py init

# 4. Add to PATH
Write-Host " Adding to User PATH..." -ForegroundColor Yellow
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($oldPath -notlike "*$currentDir*") {
    $newPath = "$oldPath;$currentDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host " Added to PATH successfully!" -ForegroundColor Green
} else {
    Write-Host " Already in PATH." -ForegroundColor Gray
}

Write-Host "`n SETUP COMPLETE!" -ForegroundColor Green
Write-Host "--------------------------------------------------"
Write-Host "1. Add your API key to: freeagentdev\config.yaml"
Write-Host "2. RESTART your terminal (to load the new PATH)"
Write-Host "3. Run 'freeagent \"task\"' from ANY folder!"
Write-Host "--------------------------------------------------"
pause
