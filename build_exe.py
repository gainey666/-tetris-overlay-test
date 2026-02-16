#!/usr/bin/env python3
"""Build script for creating Windows executable with PyInstaller."""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and handle errors."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def build_executable():
    """Build the Windows executable."""
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Install PyInstaller if not present
    print("Checking PyInstaller...")
    try:
        import PyInstaller
        print("PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command(f"{sys.executable} -m pip install pyinstaller"):
            return False
    
    # Clean previous builds
    print("Cleaning previous builds...")
    for dist_dir in ["dist", "build"]:
        if Path(dist_dir).exists():
            shutil.rmtree(dist_dir)
    
    # Create spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_overlay_core.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'pygame',
        'tinydb',
        'sqlmodel',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'cv2',
        'keyboard',
        'mss',
        'dxcam',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'scipy',
        'pandas',
        'notebook',
        'jupyter',
        'IPython',
    ],
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
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
)
'''
    
    with open('tetris_overlay.spec', 'w') as f:
        f.write(spec_content)
    
    # Build the executable
    print("Building executable...")
    if not run_command(f"{sys.executable} -m PyInstaller tetris_overlay.spec --clean"):
        return False
    
    # Create distribution folder
    dist_dir = Path("dist/TetrisOverlay")
    if not dist_dir.exists():
        print("Error: Executable not found in dist/TetrisOverlay")
        return False
    
    # Copy additional files
    additional_files = [
        'README.md',
        'requirements.txt',
        'calibration.json',
    ]
    
    print("Copying additional files...")
    for file in additional_files:
        src = Path(file)
        if src.exists():
            dst = dist_dir / file
            shutil.copy2(src, dst)
            print(f"Copied {file}")
    
    # Create a simple launcher script
    launcher_content = '''@echo off
echo Starting Tetris Overlay...
echo.
echo Press F9 to toggle overlay
echo Press F1 for settings
echo Press Ctrl+Alt+S for statistics
echo Press Esc to quit
echo.
TetrisOverlay.exe
pause
'''
    
    with open(dist_dir / 'run_overlay.bat', 'w') as f:
        f.write(launcher_content)
    
    print(f"\n✅ Build successful!")
    print(f"📦 Executable: {dist_dir.absolute()}")
    print(f"🚀 Run: {dist_dir / 'run_overlay.bat'}")
    
    return True

if __name__ == "__main__":
    print("🔨 Building Tetris Overlay Windows Executable")
    print("=" * 50)
    
    if build_executable():
        print("\n🎉 Build completed successfully!")
        print("You can now distribute the dist/TetrisOverlay folder")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)
