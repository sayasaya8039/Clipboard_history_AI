# -*- mode: python ; coding: utf-8 -*-
"""
クリップボード履歴アプリ - PyInstaller設定ファイル
"""

import sys
from pathlib import Path

# アプリケーション情報
APP_NAME = 'coppy'
APP_VERSION = '1.1.0'

# パス設定
base_path = Path(SPECPATH)
resources_path = base_path / 'resources'

a = Analysis(
    ['main.py'],
    pathex=[str(base_path)],
    binaries=[],
    datas=[
        # リソースファイル
        (str(resources_path / 'icon.ico'), 'resources'),
        (str(resources_path / 'icon.png'), 'resources'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'sqlite3',
        'hashlib',
        'uuid',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL.ImageTk',
    ],
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
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリなのでコンソール非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(resources_path / 'icon.ico'),  # アプリアイコン
    version_info=None,
)
