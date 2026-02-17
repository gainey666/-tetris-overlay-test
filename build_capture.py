#!/usr/bin/env python3
"""
Build script for the WGC capture DLL.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Build the C++ capture DLL."""
    capture_dir = Path(__file__).parent / "src" / "capture_cpp"
    build_dir = capture_dir / "build"
    
    print("🔨 Building WGC Capture DLL...")
    
    # Create build directory
    build_dir.mkdir(exist_ok=True)
    
    # Configure with CMake
    cmake_cmd = [
        "cmake",
        "-A", "x64",
        "-DCMAKE_BUILD_TYPE=Release",
        str(capture_dir)
    ]
    
    print(f"📋 Running: {' '.join(cmake_cmd)}")
    result = subprocess.run(cmake_cmd, cwd=build_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ CMake configuration failed:")
        print(result.stdout)
        print(result.stderr)
        return 1
    
    # Build with MSBuild
    build_cmd = [
        "cmake",
        "--build", str(build_dir),
        "--config", "Release"
    ]
    
    print(f"📋 Running: {' '.join(build_cmd)}")
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed:")
        print(result.stdout)
        print(result.stderr)
        return 1
    
    # Copy DLL to expected location
    dll_path = build_dir / "Release" / "capture_cpp.dll"
    target_path = capture_dir / "capture_cpp.dll"
    
    if dll_path.exists():
        import shutil
        shutil.copy2(dll_path, target_path)
        print(f"✅ DLL copied to: {target_path}")
        return 0
    else:
        print(f"❌ DLL not found at: {dll_path}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
