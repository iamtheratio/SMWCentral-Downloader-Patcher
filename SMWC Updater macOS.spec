# -*- mode: python ; coding: utf-8 -*-
# macOS-specific PyInstaller spec for SMWC Updater

import platform

# Build a single-arch app matching the current machine (avoids universal2 issues when
# the Python installation and/or extension modules are not fat/universal binaries).
_machine = platform.machine()
_target_arch = _machine if _machine in ("x86_64", "arm64") else None
a = Analysis(
    ['standalone_updater.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SMWC Updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=_target_arch,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='SMWC Updater.app',
    icon='assets/icon.icns',  # Use proper .icns file for macOS
    bundle_identifier='com.iamtheratio.smwc-updater',
    version='4.8.0',
    info_plist={
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
        'CFBundleDisplayName': 'SMWC Updater',
        'CFBundleShortVersionString': '4.8.0',
        'CFBundleVersion': '4.8.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)
