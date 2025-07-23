# -*- mode: python ; coding: utf-8 -*-
# macOS-specific PyInstaller spec for SMWC Downloader

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('ui', 'ui')],
    hiddenimports=['tkinter.filedialog', 'tkinter.messagebox'],
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
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='SMWC Downloader.app',
    icon='assets/icon.ico',
    bundle_identifier='com.iamtheratio.smwc-downloader',
    version='4.4.0',
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
