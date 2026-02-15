# Tetris Overlay - Real-time Best Move Predictor

A high-performance C++ overlay that predicts optimal Tetris piece placements using only visual information. Achieves sub-5ms latency for the complete capture-to-ghost pipeline.

## Prerequisites

- Windows 10/11 (x64)
- Visual Studio 2019 or 2022 with C++17 support
- CMake 3.15 or higher
- Git

## Install Dependencies

Using vcpkg (recommended):

```bash
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install
.\vcpkg install opencv[core]:x64-windows d3d11 dxgi direct2d onnxruntime
```

## Build

```bash
# From the tetris_overlay directory
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=[path_to_vcpkg]/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
```

Or open the generated Visual Studio solution in `build/TetrisOverlay.sln`.

## Calibration

First-time setup requires calibrating the game board region:

```bash
# Run the calibration utility
build\Release\tetris_overlay.exe --calibrate
```

1. A window will show your current screen capture
2. Click the top-left corner of the Tetris board
3. Click the bottom-right corner of the Tetris board
4. The ROI is saved to `calibration.json`

## Run

```bash
build\Release\tetris_overlay.exe
```

The overlay will:
- Capture the screen using DXGI Desktop Duplication
- Extract the 20×10 binary board matrix
- Predict the optimal piece placement
- Draw a semi-transparent yellow ghost piece at the suggested position
- Press ESC to quit

## Expected Behavior

- A yellow outline appears showing where to place the current piece
- The ghost updates in real-time as pieces fall
- Latency should be <5ms per frame (≈200+ FPS)
- The overlay window is click-through and always on top

## Performance Test

The program automatically runs a 200ms benchmark on startup and prints:

```
Capture   : 0.94 ms
Board proc: 0.38 ms
Predict   : 0.71 ms
Overlay   : 0.31 ms
Total per frame: 2.34 ms (≈ 430 FPS)
```

If any stage exceeds 5ms, the implementation may need optimization.

## Optional: CNN Model

Place a trained ONNX model named `tetris_cnn.onnx` in the executable directory to use neural network predictions instead of the handcrafted heuristic.

## Troubleshooting

- **DXGI errors**: Ensure the game is running in windowed or borderless mode
- **High latency**: Check that vcpkg libraries are built in Release mode
- **Overlay not visible**: Verify the game isn't in exclusive fullscreen mode
- **Calibration issues**: Make sure to click exactly on the board corners

## Architecture

- **FrameGrabber**: DXGI Desktop Duplication for screen capture
- **BoardExtractor**: OpenCV HSV thresholding + morphological operations
- **HeuristicEngine**: Weighted-sum evaluation or optional CNN
- **OverlayRenderer**: Direct2D transparent click-through window
