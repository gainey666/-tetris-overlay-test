# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_overlay_core.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('assets', 'assets')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'pygame', 'tinydb', 'sqlmodel', 'matplotlib', 'matplotlib.backends.backend_qt5agg'],
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
    name='TetrisOverlay',
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
)
