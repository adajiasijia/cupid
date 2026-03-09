@echo off
REM Backend Service Startup Script (Using Local Python Embedded)

echo ========================================
echo Licai Backend Service
echo ========================================
echo.

cd /d "%~dp0"

REM Check if local Python is installed
if not exist "python_embed\python.exe" (
    echo ERROR: Local Python environment not found.
    echo.
    echo Please run install_python.bat first to install Python.
    echo.
    pause
    exit /b 1
)

REM Set Python command
set PYTHON_CMD=python_embed\python.exe

REM Check if dependencies are installed
if not exist "python_embed\Lib\site-packages\flask" (
    echo First run: Installing dependencies...
    echo.
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
)

REM Create data directory
if not exist "data" (
    mkdir data
)

REM Start service
echo Starting backend service...
echo Service URL: http://localhost:5000
echo API Docs: http://localhost:5000/api
echo Database: SQLite (Embedded)
echo.
echo Press Ctrl+C to stop the service
echo ========================================
echo.

%PYTHON_CMD% app.py

pause
