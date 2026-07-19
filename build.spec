# -*- mode: python ; coding: utf-8 -*-
"""Spécification PyInstaller — MD Reader (.exe, onefile, windowed).

QtWebEngine (Chromium) est embarqué via les hooks PySide6 de PyInstaller. En cas
d'échec du mode onefile avec QtWebEngine (extraction de QtWebEngineProcess), passer
en mode onedir : remplacer le bloc EXE ci-dessous par EXE(exclude_binaries=True) + COLLECT.
"""

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("resources", "resources")],
    hiddenimports=[],
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
    name="MD Reader",
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
    icon="resources/icon.ico",
)
