#!/bin/bash
# SMWC Downloader Launcher
# Bypasses macOS app bundle issues by running the executable directly

cd "$(dirname "$0")"

# Find the executable
EXECUTABLE="dist/SMWC Downloader.app/Contents/MacOS/SMWC Downloader"

if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ SMWC Downloader executable not found"
    exit 1
fi

echo "🚀 Launching SMWC Downloader..."

# Launch the executable directly
exec "$EXECUTABLE"
