@echo off
REM ProShop - Windows Quick Start Script
REM This script sets up and starts the application

echo.
echo ========================================
echo   ProShop E-Commerce Application
echo   Windows Setup & Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Remember to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Navigate to backend folder
cd backend

REM Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ========================================
echo   Starting Flask Server
echo ========================================
echo.
echo Backend Server: http://localhost:5000
echo Frontend: Open frontend/index.html in your browser
echo.
echo Login Credentials:
echo   Admin: admin / admin123
echo   Customer: 9876543210 / 123456
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
