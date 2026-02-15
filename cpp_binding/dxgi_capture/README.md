# DXGI Capture Module

This directory contains a placeholder pybind11 module that will wrap a Windows DXGI Desktop Duplication capture path. The current implementation only provides the module skeleton; the actual GPU capture logic still needs to be filled in.

## Layout

- `dxgi_frame_grabber.h/.cpp` – C++ interface for a DXGI-based frame grabber.
- `pybind_module.cpp` – pybind11 bindings exposing the `FrameGrabber` class to Python.
- `CMakeLists.txt` – builds the `dxgi_capture` extension, linking against DirectX 11 and OpenCV.

## Building

Use the same PowerShell helper pattern as the board processor (call `VsDevCmd.bat`, run CMake with the vcpkg toolchain, and invoke `nmake`).

```
cmake .. -G "NMake Makefiles" \
    -DCMAKE_TOOLCHAIN_FILE=".../vcpkg/scripts/buildsystems/vcpkg.cmake" \
    -DOpenCV_DIR=".../vcpkg/installed/x64-windows/share/opencv4"
nmake
```

> **Note:** The current implementation does **not** yet hook into DXGI. It only establishes the scaffolding so the capture logic can be filled in later.
