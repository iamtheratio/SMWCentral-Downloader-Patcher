# GitHub Actions Build Instructions

This repository includes automated GitHub Actions workflows to build releases for Windows, macOS, and Linux.

## Workflow Files

### 1. `dev-builds.yml` - Development Builds
- **Trigger**: Push to `main` or `develop` branches
- **Purpose**: Quick tests and validation
- **Platforms**: Windows, macOS, Linux (test builds only)
- **Artifacts**: None (testing only)

### 2. `release.yml` - Release Builds  
- **Trigger**: Push version tags (e.g., `v4.3.0`) or manual dispatch
- **Purpose**: Create official releases with binaries
- **Platforms**: Windows, macOS, Linux (full builds)
- **Artifacts**: Platform-specific executables uploaded to GitHub Releases

### 3. `build-releases.yml` - Comprehensive Builds
- **Trigger**: Push to `main`, version tags, or manual dispatch  
- **Purpose**: Full build pipeline with artifacts
- **Platforms**: Windows, macOS, Linux
- **Artifacts**: Stored as GitHub artifacts (30 days retention)

## How to Create a Release

### Method 1: Tag-based Release (Recommended)
1. Update the version in `main.py`:
   ```python
   VERSION = "v4.4.0"  # Update this
   ```

2. Commit and push to main:
   ```bash
   git add main.py
   git commit -m "Release v4.4.0"
   git push origin main
   ```

3. Create and push a version tag:
   ```bash
   git tag v4.4.0
   git push origin v4.4.0
   ```

4. GitHub Actions will automatically:
   - Build for all 3 platforms
   - Create a GitHub Release
   - Upload the executables as release assets

### Method 2: Manual Release
1. Go to GitHub Actions tab in your repository
2. Select "Release" workflow
3. Click "Run workflow"
4. Enter the version tag (e.g., `v4.4.0`)
5. Click "Run workflow"

## Build Outputs

### Windows
- **File**: `SMWC-Downloader-v4.4.0-Windows-x64.zip`
- **Contents**: `SMWC Downloader.exe` + dependencies
- **Requirements**: Windows 10+ (64-bit)

### macOS  
- **File**: `SMWC-Downloader-v4.4.0-macOS-Universal.dmg`
- **Contents**: `SMWC Downloader.app` (Universal Binary)
- **Requirements**: macOS 10.15+ (Intel + Apple Silicon)

### Linux
- **File**: `SMWC-Downloader-v4.4.0-Linux-x64.tar.gz`
- **Contents**: `smwc-downloader` executable
- **Requirements**: Modern Linux distribution with GTK

## Build Configuration

### PyInstaller Specs
Each platform uses a custom PyInstaller spec file:
- **Windows**: Uses existing `SMWC Downloader.spec`
- **macOS**: Creates universal binary with app bundle
- **Linux**: Creates standalone executable

### Dependencies
All platforms install:
- Python 3.11
- Requirements from `requirements.txt`
- PyInstaller for building executables

### Platform-Specific Notes

**Windows:**
- Uses `windows-latest` runner (Windows Server 2022)
- Creates ZIP archive with executable
- UPX compression disabled to avoid antivirus issues

**macOS:**
- Uses `macos-latest` runner
- Creates universal binary (`target_arch='universal2'`)
- Packages as DMG with Applications symlink
- Optional code signing support (requires certificates)

**Linux:**
- Uses `ubuntu-latest` runner
- Installs `python3-tk` and `python3-dev`
- Creates tarball with executable
- Should work on most modern Linux distributions

## Secrets Configuration (Optional)

For enhanced builds, you can add these secrets to your repository:

### Apple Code Signing (macOS)
- `APPLE_CERTIFICATE_BASE64`: Base64-encoded developer certificate
- `APPLE_CERTIFICATE_PASSWORD`: Certificate password
- `APPLE_TEAM_ID`: Apple Developer Team ID

### Adding Secrets
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add the secret name and value

## Troubleshooting

### Common Issues

**Build Fails on Import Errors:**
- Check `requirements.txt` includes all dependencies
- Verify hidden imports in PyInstaller spec files

**Windows Antivirus Issues:**
- UPX is disabled to reduce false positives
- Users may still need to add exclusions

**macOS Gatekeeper Issues:**
- Add code signing certificates for trusted distribution
- Users need to right-click → Open for unsigned apps

**Linux Missing Dependencies:**
- Workflow installs `python3-tk` automatically
- Users may need additional packages on some distributions

### Testing Locally

Before pushing tags, test builds locally:

```bash
# Install PyInstaller
pip install pyinstaller

# Test Windows build
pyinstaller "SMWC Downloader.spec" --clean

# Test macOS build (on macOS)
pyinstaller "SMWC Downloader macOS.spec" --clean

# Test Linux build (on Linux)
pyinstaller "SMWC Downloader Linux.spec" --clean
```

## Workflow Status

Monitor build progress:
1. Go to GitHub Actions tab
2. Click on the running workflow
3. View logs for each platform build
4. Download artifacts or check releases page

The workflows are designed to be robust and handle platform differences automatically.
