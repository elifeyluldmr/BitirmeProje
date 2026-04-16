param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = 'Stop'

$body = @{
    text = "Urgent: Verify your password immediately to avoid account lock."
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BaseUrl/predict" -Method Post -ContentType "application/json" -Body $body

Write-Host "Prediction response:"
$response | ConvertTo-Json -Depth 3
