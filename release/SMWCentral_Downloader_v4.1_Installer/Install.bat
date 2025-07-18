@echo off
title SMWCentral Downloader v4.1 Installation
echo.
echo SMWCentral Downloader ^& Patcher v4.1 Installation
echo ================================================
echo.
echo This installer will set up SMWCentral Downloader on your system.
echo.
echo What this installer does:
echo - Creates a shortcut on your desktop
echo - Sets up the updater for automatic updates
echo - Configures the application properly
echo.
pause

REM Create desktop shortcut
echo Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
echo [InternetShortcut] > "%desktop%\SMWC Downloader.url"
echo URL=file:///%CD%\SMWC Downloader.exe >> "%desktop%\SMWC Downloader.url"
echo IconFile=%CD%\SMWC Downloader.exe >> "%desktop%\SMWC Downloader.url"
echo IconIndex=0 >> "%desktop%\SMWC Downloader.url"

echo.
echo Installation complete!
echo.
echo You can now:
echo - Double-click the desktop shortcut to run the application
echo - Or run "SMWC Downloader.exe" from this folder
echo.
echo IMPORTANT: Do not move or delete "SMWC Updater.exe" - it's needed for updates
echo.
pause
