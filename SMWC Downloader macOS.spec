# -*- mode: python ; coding: utf-8 -*-
# macOS-specific PyInstaller spec for SMWC Downloader

import platform

# Build a single-arch app matching the current machine (avoids universal2 issues when
# the Python installation and/or extension modules are not fat/universal binaries).
_machine = platform.machine()
_target_arch = _machine if _machine in ("x86_64", "arm64") else None
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('ui', 'ui')],
    hiddenimports=['tkinter.filedialog', 'tkinter.messagebox', 'platform_utils', 'difficulty_migration', 'difficulty_lookup_manager'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL', 'websockets.speedups'],  # Exclude native speedups that cause universal2 issues
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SMWC Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=_target_arch,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='SMWC Downloader.app',
    icon='assets/icon.icns',  # Use proper .icns file for macOS
    bundle_identifier='com.iamtheratio.smwc-downloader',
    version='4.9.0',
    info_plist={
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
        'CFBundleDisplayName': 'SMWC Downloader & Patcher',
        'CFBundleName': 'SMWC Downloader & Patcher',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        }
    }
)
