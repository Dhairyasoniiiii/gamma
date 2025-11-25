@echo off
cd /d "C:\Users\PC\OneDrive\Desktop\gamma clone"
set PYTHONPATH=C:\Users\PC\OneDrive\Desktop\gamma clone

echo.
echo ============================================
echo    GAMMA CLONE BACKEND SERVER
echo ============================================
echo.
echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

C:\Python39\python.exe backend\main.py

pause
