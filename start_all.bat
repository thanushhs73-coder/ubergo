@echo off
REM UBERGO_B2 Startup Script for Windows PowerShell

REM This script starts all four main apps in separate terminal windows

cd /d "%~dp0"

echo Starting UBERGO_B2 system...
echo.

REM Start Admin Dashboard (Port 8000)
echo Starting Admin Dashboard on Port 8000...
start cmd /k "cd /d %cd% && python -m uvicorn admin_app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak

REM Start User Launcher (Port 8001)
echo Starting User Launcher on Port 8001...
start cmd /k "cd /d %cd% && python -m uvicorn user_launcher.main:app --host 127.0.0.1 --port 8001 --reload"

timeout /t 2 /nobreak

REM Start Driver Launcher (Port 8900)
echo Starting Driver Launcher on Port 8900...
start cmd /k "cd /d %cd% && python -m uvicorn driver_launcher.main:app --host 127.0.0.1 --port 8900 --reload"

timeout /t 2 /nobreak

echo.
echo UBERGO_B2 system started!
echo.
echo Access points:
echo   Admin Dashboard:   http://localhost:8000
echo   User Launcher:     http://localhost:8001
echo   Driver Launcher:   http://localhost:8900
echo.
echo Note: User and driver instances will be spawned dynamically when created.
echo.
pause
