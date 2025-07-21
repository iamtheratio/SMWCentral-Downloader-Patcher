# macOS Build & Distribution Guide

## Prerequisites

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install PyInstaller (if not already installed)
```bash
pip install pyinstaller
```

### 3. Install create-dmg (optional, for DMG installer)
```bash
brew install create-dmg
```

## Building for macOS

### Quick Build
```bash
python build_release_macos.py
```

This will:
1. Build both main app and updater as `.app` bundles
2. Create a release ZIP with proper directory structure  
3. Optionally create a DMG installer

### Manual Build Steps

#### 1. Build Main Application
```bash
pyinstaller --clean "SMWC Downloader macOS.spec"
```

#### 2. Build Updater
```bash
pyinstaller --clean "SMWC Updater macOS.spec"
```

#### 3. Package Release
```bash
python build_release_macos.py
```

## Testing the macOS Build

### 1. Test Locally
```bash
# Run the built app
open "dist/SMWC Downloader.app"
```

### 2. Test Update System
1. Create a test release on GitHub with macOS asset
2. Run the app and trigger an update check
3. Verify it downloads the macOS-specific asset

### 3. Test on Different macOS Versions
- macOS 10.14 (Mojave) - minimum supported version
- macOS 11 (Big Sur) 
- macOS 12 (Monterey)
- macOS 13 (Ventura)
- macOS 14 (Sonoma)

## Distribution Strategy

### 1. GitHub Releases
Upload these files to each GitHub release:

- `SMWC_Downloader_v4.4_Windows.zip` (Windows users)
- `SMWC_Downloader_v4.4_macOS.zip` (macOS users)
- `SMWC_Downloader_v4.4.zip` (generic fallback)

### 2. Asset Naming Convention
The updater looks for these patterns:
- **macOS**: assets containing "macos", "mac", or "darwin"
- **Windows**: assets containing "win" or "windows"

### 3. Release Notes Template
```markdown
# SMWCentral Downloader v4.4 - Cross-Platform Release

## 🎉 NEW: macOS Support!
- Native macOS .app bundle
- Automatic macOS-specific updates
- Full feature parity with Windows version

## Features
- [List existing features]

## Download
- **Windows**: [SMWC_Downloader_v4.4_Windows.zip]
- **macOS**: [SMWC_Downloader_v4.4_macOS.zip]

## Installation
### Windows
1. Extract ZIP file
2. Run `SMWC Downloader.exe`

### macOS  
1. Extract ZIP file
2. Move `SMWC Downloader.app` to Applications folder
3. Right-click → Open (first time only)
```

## Troubleshooting

### macOS Security Warnings
Users may see "App can't be opened because it's from an unidentified developer"

**Solution for users:**
1. System Preferences → Security & Privacy → General
2. Click "Open Anyway" 
3. Or right-click app → "Open"

### Code Signing (Future Enhancement)
For professional distribution, consider:
```bash
# Get Apple Developer certificate
# Sign the application
codesign --deep --sign "Developer ID Application: Your Name" "SMWC Downloader.app"

# Notarize with Apple
xcrun notarytool submit "SMWC Downloader.app.zip" --keychain-profile "notarytool-profile"
```

### Build Errors

#### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

#### PyInstaller issues
```bash
pip install --upgrade pyinstaller
pyinstaller --clean "SMWC Downloader macOS.spec"
```

#### Permission errors
```bash
chmod +x build_release_macos.py
python build_release_macos.py
```

## Quality Assurance Checklist

### Pre-Release Testing
- [ ] App launches without errors
- [ ] All UI elements display correctly
- [ ] Download functionality works
- [ ] Patching functionality works  
- [ ] Settings save/load properly
- [ ] Update system detects macOS releases
- [ ] Update process completes successfully
- [ ] App works on different macOS versions

### Cross-Platform Testing
- [ ] Windows users still get Windows updates
- [ ] macOS users get macOS updates
- [ ] Fallback system works if platform detection fails
- [ ] No breaking changes for existing users

## File Structure

After building, your release directory should look like:
```
release/
├── SMWC Downloader v4.4 macOS/
│   ├── SMWC Downloader.app/
│   ├── updater/
│   │   └── SMWC Updater.app/
│   ├── config.json
│   └── README.md
└── SMWC_Downloader_v4.4_macOS.zip
```

## Success Metrics

Your macOS build is ready when:
- ✅ Builds complete without errors  
- ✅ .app bundles launch normally
- ✅ Core functionality works identically to Windows
- ✅ Updates download correct platform assets
- ✅ No regressions for Windows users
- ✅ File sizes are reasonable (~20-30MB for main app)

## Next Steps

1. **Test thoroughly** on multiple macOS versions
2. **Create first dual-platform release** (v4.4)
3. **Monitor user feedback** for platform-specific issues
4. **Consider code signing** for better user experience
5. **Update documentation** to reflect macOS support
