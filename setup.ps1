# DocuMind AI — Windows setup helper
# Usage: powershell -ExecutionPolicy Bypass -File .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "== DocuMind AI setup ==" -ForegroundColor Cyan

# 1. Environment files
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created root .env" -ForegroundColor Green
}
if (-not (Test-Path "backend/.env")) {
    Copy-Item "backend/.env.example" "backend/.env"
    Write-Host "Created backend/.env" -ForegroundColor Green
}

Write-Host ""
Write-Host "Environment files ready." -ForegroundColor Green
Write-Host "IMPORTANT: edit SECRET_KEY in .env before any real deployment." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start Docker Desktop"
Write-Host "  2. docker compose up -d --build"
Write-Host "  3. docker compose exec ollama ollama pull qwen2.5:3b"
Write-Host "  4. Open http://localhost:8080"
