# Gamma Clone - Stable Server Start (No Reload)
# Use this if auto-reload is causing issues

$env:PYTHONPATH = "C:\Users\PC\OneDrive\Desktop\gamma clone"

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "[GAMMA CLONE] Starting Backend Server" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan
Write-Host "Mode:     STABLE (no auto-reload)" -ForegroundColor Yellow
Write-Host "Database: SQLite local" -ForegroundColor White
Write-Host "Server:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "`nPress CTRL+C to stop`n" -ForegroundColor Yellow

# Start without reload for stability
C:/Python39/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level info
