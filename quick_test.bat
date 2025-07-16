@echo off
REM Quick test runner for specific modules or during development
REM Usage: quick_test.bat [module_name]
REM Example: quick_test.bat test_utils

if "%1"=="" (
    echo Running a quick subset of tests...
    python -m tests.run_tests --module test_utils
    python -m tests.run_tests --module test_config_manager
) else (
    echo Running specific test module: %1
    python -m tests.run_tests --module %1
)

pause
