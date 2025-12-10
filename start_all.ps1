# UBERGO_B2 Startup Script for PowerShell
# This script starts all main apps in separate PowerShell windows

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Starting UBERGO_B2 system..." -ForegroundColor Green
Write-Host ""

# Admin Dashboard (Port 8000)
Write-Host "Starting Admin Dashboard on Port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; python -m uvicorn admin_app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Sleep -Seconds 2

# User Launcher (Port 8001)
Write-Host "Starting User Launcher on Port 8001..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; python -m uvicorn user_launcher.main:app --host 127.0.0.1 --port 8001 --reload"
Start-Sleep -Seconds 2

# Driver Launcher (Port 8900)
Write-Host "Starting Driver Launcher on Port 8900..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; python -m uvicorn driver_launcher.main:app --host 127.0.0.1 --port 8900 --reload"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "UBERGO_B2 system started!" -ForegroundColor Green
Write-Host ""
Write-Host "Access points:" -ForegroundColor Yellow
Write-Host "  Admin Dashboard:   http://localhost:8000"
Write-Host "  User Launcher:     http://localhost:8001"
Write-Host "  Driver Launcher:   http://localhost:8900"
Write-Host ""
Write-Host "Note: User and driver instances will be spawned dynamically when created." -ForegroundColor Gray
