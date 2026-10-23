$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

Write-Host "=================================================================="
Write-Host "  Telecom Nexus - Antigravity Workshop Environment Installer"
Write-Host "=================================================================="

if (-not (Test-Path ".venv")) {
    Write-Host "[1/3] Creating Python virtual environment (.venv)..."
    python -m venv .venv
} else {
    Write-Host "[1/3] Using existing Python virtual environment (.venv)..."
}

Write-Host "[2/3] Installing Python dependencies..."
.\.venv\Scripts\pip install --quiet --upgrade pip
.\.venv\Scripts\pip install --quiet -r requirements.txt

Write-Host "[3/3] Seeding deterministic 3GPP RAN, TAP3 CDR & B2B SLA database..."
.\.venv\Scripts\python data/seed_telecom_data.py

Write-Host ""
Write-Host "Setup complete! Start the live Telecom NOC Dashboard anytime with:"
Write-Host "  .\.venv\Scripts\uvicorn src.main:app --reload --port 8001"
Write-Host "=================================================================="
