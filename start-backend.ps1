# Gamma Clone Backend - Start Script
# Run this to start the backend server

$env:PYTHONPATH = "C:\Users\PC\OneDrive\Desktop\gamma clone"
Write-Host "`n==============================================`n" -ForegroundColor Cyan
Write-Host "[STARTUP] Starting Gamma Clone Backend`n" -ForegroundColor Green
Write-Host "==============================================`n" -ForegroundColor Cyan
Write-Host "Database: SQLite local" -ForegroundColor White
Write-Host "Server:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server`n" -ForegroundColor Yellow

# Exclude database files and cache from file watching to prevent unwanted reloads
C:/Python39/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "*.db" --reload-exclude "*.db-journal" --reload-exclude "__pycache__/*"
