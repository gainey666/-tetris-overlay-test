# Tetris Overlay Project - Complete State Documentation

## 📋 Project Overview
**Project Name**: Tetris Overlay  
**Type**: Real-time Tetris best-move prediction overlay  
**Language**: C++17  
**Platform**: Windows 10+  
**Build System**: CMake 3.15+  
**Package Manager**: vcpkg  

## 🎯 Project Objective
Create a real-time overlay that:
- Captures the screen using DXGI Desktop Duplication
- Extracts Tetris board state using OpenCV image processing
- Predicts best moves using heuristic evaluation (with optional ONNX Runtime CNN)
- Renders transparent overlay showing ghost piece using Direct2D
- Provides calibration utility to define board ROI

## 📁 Current Project Structure
```
tetris_overlay/
├── src/
│   ├── main.cpp                    # Entry point (IN PROGRESS)
│   ├── frame_grabber.h/.cpp        # DXGI screen capture (COMPLETED)
│   ├── board_extractor.h/.cpp      # OpenCV board processing (COMPLETED)
│   ├── heuristic_engine.h/.cpp     # Move prediction (NEEDS COMPLETION)
│   ├── overlay_renderer.h/.cpp     # Direct2D overlay (NEEDS COMPLETION)
│   ├── calibrate.h/.cpp            # Board calibration (NEEDS COMPLETION)
│   └── utils.h                     # Timer utilities (COMPLETED)
├── CMakeLists.txt                  # Build configuration (COMPLETED)
├── calibration.json               # Board ROI data (PLACEHOLDER)
├── build/                          # Build directory
└── PROJECT_COMPLETE_STATE.md       # This file
```

## 🔧 Dependencies Status
- **OpenCV**: ❌ NOT INSTALLED (vcpkg build failing)
- **DirectX/Direct2D**: ✅ Available via Windows SDK
- **nlohmann-json**: ✅ Available via vcpkg
- **ONNX Runtime**: ❌ NOT INSTALLED (optional)

## 🚨 Current Blocking Issue
**vcpkg OpenCV installation failing** - Multiple attempts with different feature combinations all fail during build. Error appears to be related to missing dependencies (pkg-config was installed but build still fails).

## 📝 Completed Files Status

### ✅ FULLY COMPLETED
1. **utils.h** - Simple RAII timer class
2. **frame_grabber.h/.cpp** - DXGI Desktop Duplication capture
3. **board_extractor.h/.cpp** - OpenCV HSV thresholding and board extraction
4. **CMakeLists.txt** - Full vcpkg integration with fallback logic

### 🔄 IN PROGRESS / NEEDS COMPLETION
1. **main.cpp** - Entry point skeleton exists, needs completion
2. **heuristic_engine.h/.cpp** - Header exists, implementation needs completion
3. **overlay_renderer.h/.cpp** - Header exists, implementation needs completion
4. **calibrate.h/.cpp** - Header exists, implementation needs completion

## 🎯 Next Immediate Tasks
1. **Resolve vcpkg OpenCV installation** (CRITICAL BLOCKER)
2. **Complete remaining source files** once OpenCV is working
3. **Test full build and functionality**

## 📋 Detailed File Specifications

### utils.h
```cpp
#pragma once
#include <chrono>
#include <iostream>

/** Simple RAII timer that prints elapsed time when it goes out of scope. */
class ScopedTimer {
public:
    explicit ScopedTimer(const char* name) : m_name(name), m_start(std::chrono::high_resolution_clock::now()) {}
    ~ScopedTimer() {
        auto end = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(end - m_start).count();
        std::cout << "[" << m_name << "] " << ms << " ms\n";
    }
private:
    const char* m_name;
    std::chrono::high_resolution_clock::time_point m_start;
};
```

### frame_grabber.h/.cpp
- Uses DXGI Desktop Duplication API
- Captures primary monitor in BGRA format
- Zero-copy mapping to cv::Mat
- COM objects: IDXGIFactory2, IDXGIOutputDuplication, ID3D11Device, ID3D11DeviceContext, ID3D11Texture2D

### board_extractor.h/.cpp
- HSV color thresholding for block detection
- Morphological operations for cleanup
- Down-sampling to 20x10 binary matrix
- cv::Mat output (CV_8U, values 0/1)

### CMakeLists.txt
- vcpkg toolchain integration
- OpenCV find_package with fallback
- DirectX/Direct2D linking
- Optional ONNX Runtime support
- Post-build DLL copying

## 🔧 Build Commands
```powershell
# From project root
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
```

## 🐛 Known Issues & Solutions Attempted

### vcpkg OpenCV Build Failures
**Attempted Solutions:**
- Clean vcpkg state (remove, git pull, bootstrap)
- Install pkgconf dependency
- Different feature combinations (core, highgui, calib3d)
- Various command line flags

**Current Error Pattern:**
- CMake configuration fails during OpenCV build
- Missing dependencies or configuration issues
- Build fails at ninja/MSBuild stage

### Alternative Solutions Available
1. **Option A**: Continue vcpkg troubleshooting (recommended)
2. **Option B**: Use pre-built OpenCV binaries from opencv.org
3. **Option C**: Create minimal skeleton without OpenCV first

## 🎮 Usage Workflow (Once Complete)
1. **Calibration**: `tetris_overlay.exe calibrate`
   - Click top-left and bottom-right of Tetris board
   - Creates calibration.json with ROI coordinates

2. **Run Overlay**: `tetris_overlay.exe`
   - Captures screen continuously
   - Extracts board state
   - Predicts best move
   - Renders ghost piece overlay

## 📊 Technical Architecture

### Data Flow
1. **FrameGrabber** → DXGI capture → cv::Mat (BGRA)
2. **BoardExtractor** → ROI crop → HSV threshold → 20x10 binary matrix
3. **HeuristicEngine** → Board matrix → Move evaluation → Best move
4. **OverlayRenderer** → Ghost piece coordinates → Direct2D transparent overlay

### Key Classes
- **FrameGrabber**: DXGI screen capture
- **BoardExtractor**: OpenCV image processing
- **HeuristicEngine**: Move prediction (heuristic + optional CNN)
- **OverlayRenderer**: Direct2D transparent overlay
- **Calibrator**: Interactive ROI selection

## 🔄 Development Status

### Phase 1: Core Infrastructure ✅
- DXGI capture setup
- OpenCV processing pipeline
- CMake build system
- Basic utilities

### Phase 2: Application Logic 🔄
- Heuristic evaluation (IN PROGRESS)
- Direct2D overlay rendering (NEEDS START)
- Calibration utility (NEEDS START)
- Main application loop (NEEDS COMPLETION)

### Phase 3: Integration & Testing ⏳
- Full build verification
- Performance benchmarking
- Real-world testing
- Bug fixes and optimization

## 📝 Implementation Notes

### Board Representation
- 20 rows × 10 columns (standard Tetris)
- Binary matrix: 1 = block, 0 = empty
- Row 0 = top of board, Row 19 = bottom

### Piece Types
- Standard Tetris pieces (I, O, T, S, Z, J, L)
- Ghost piece shows predicted landing position
- Color-coded visualization

### Performance Targets
- < 16ms total latency (60 FPS)
- < 5ms capture time
- < 5ms processing time
- < 1ms overlay rendering

## 🚀 Quick Start for New Developer

### Prerequisites
- Visual Studio 2022 with Desktop development with C++
- Windows 10 SDK
- Git
- CMake 3.15+

### Setup Commands
```powershell
# Clone vcpkg (if not exists)
git clone https://github.com/Microsoft/vcpkg.git ../vcpkg
cd ../vcpkg
.\bootstrap-vcpkg.bat
vcpkg integrate install

# Install dependencies (when OpenCV issue resolved)
vcpkg install opencv4[core,highgui]:x64-windows nlohmann-json:x64-windows

# Build project
cd ../tetris_overlay
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build . --config Release
```

### Critical Path to Completion
1. **Resolve OpenCV installation** (BLOCKING)
2. **Complete heuristic_engine.cpp** - implement move evaluation
3. **Complete overlay_renderer.cpp** - Direct2D transparent window
4. **Complete calibrate.cpp** - Interactive ROI selection
5. **Complete main.cpp** - Application orchestration
6. **Test and debug** - Full integration testing

## 🎯 Success Criteria
- [ ] Clean vcpkg build with all dependencies
- [ ] Successful screen capture and board extraction
- [ ] Accurate move prediction
- [ ] Transparent overlay rendering
- [ ] Calibration workflow
- [ ] < 16ms end-to-end latency
- [ ] Stable real-time operation

## 📞 Support Information
This project uses Windows-specific APIs (DXGI, Direct2D) and is designed for Windows 10+ only. Cross-platform compatibility is not a goal.

## 🔄 Last Updated
**Date**: 2026-02-14  
**Status**: Core infrastructure complete, blocked by OpenCV vcpkg installation  
**Next Action**: Resolve vcpkg OpenCV build issues or switch to pre-built binaries
