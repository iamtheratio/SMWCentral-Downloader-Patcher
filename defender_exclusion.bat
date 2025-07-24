@echo off
echo Adding Windows Defender exclusions for SMWC Downloader...
echo.
echo This will add exclusions for:
echo - The project directory
echo - The built executable
echo - Common ROM directories
echo.
pause
echo.

REM Add exclusion for project directory
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0'"
echo Added exclusion for project directory: %~dp0

REM Add exclusion for dist directory
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0dist'"
echo Added exclusion for dist directory

REM Add exclusion for build directory  
powershell -Command "Add-MpPreference -ExclusionPath '%~dp0build'"
echo Added exclusion for build directory

REM Add exclusion for the executable name pattern
powershell -Command "Add-MpPreference -ExclusionProcess 'SMWC Downloader*.exe'"
echo Added exclusion for SMWC Downloader executables

echo.
echo Exclusions added successfully!
echo You may need to run this as Administrator if you got permission errors.
echo.
pause
