$ErrorActionPreference = 'Stop'

if (-not (Test-Path "data/emails.csv")) {
    Copy-Item "data/emails.sample.csv" "data/emails.csv"
    Write-Host "Created data/emails.csv from sample template."
}

Write-Host "Training model..."
python src/train.py

Write-Host "Starting API on http://127.0.0.1:8000 ..."
uvicorn app.main:app --reload
