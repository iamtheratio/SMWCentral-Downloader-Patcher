# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README.md', '.'),
        ('images', 'images'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'requests',
        'sv_ttk',
        'pywinstyles',
        'bps',
        'ips_util',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'ui',
        'ui.components',
        'ui.layout',
        'ui.navigation',
        'ui.page_manager',
        'ui.theme_controls',
        'ui.version_display',
        'ui.bulk_download_components',
        'ui.hack_history_components',
        'ui.pages',
        'ui.pages.bulk_download_page',
        'ui.pages.hack_history_page',
        'ui.components.inline_editor',
        'ui.components.table_filters',
        'hack_data_manager',
        'migration_manager',
        'api_pipeline',
        'config_manager',
        'logging_system',
        'patch_handler',
        'patcher_bps',
        'patcher_ips',
        'smwc_api_proxy',
        'utils',
        'colors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SMWC Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
    icon='assets/icon.ico'
)