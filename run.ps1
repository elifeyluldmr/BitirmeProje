$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python not found at $venvPython"
}

if (-not (Test-Path "data/emails.csv")) {
    Copy-Item "data/emails.sample.csv" "data/emails.csv"
    Write-Host "Created data/emails.csv from sample template."
}

Write-Host "Training model..."
& $venvPython "src/train_model.py"

Write-Host "Starting API on http://127.0.0.1:8000 ..."
& $venvPython -m uvicorn app.main:app --reload
