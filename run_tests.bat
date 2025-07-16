@echo off
REM Batch file to run all tests with coverage for SMWCentral Downloader & Patcher
REM Usage: run_tests.bat

echo SMWCentral Downloader ^& Patcher - Test Suite
echo =============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Install test requirements if coverage is missing
python -c "import coverage" >nul 2>&1
if errorlevel 1 (
    echo Installing test requirements...
    pip install coverage
)

REM Run tests using the custom test runner
echo Running unit tests...
python -m tests.run_tests

REM Check if pytest is available for alternative test runner
python -c "import pytest" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo Alternative: Running with pytest...
    pytest
)

echo.
echo Test execution completed.
pause
