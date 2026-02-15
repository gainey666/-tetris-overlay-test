Below is a complete “LLM‑ready prompt package” that you can copy‑paste into any LLM (ChatGPT, Claude, Gemini, Llama‑2, etc.) and it will automatically generate a fully‑working, low‑latency Tetris‑prediction overlay exactly as described in the earlier answer.

The package consists of three parts:

High‑level brief – tells the LLM what the project is, which language to use, and which libraries are mandatory.
File‑by‑file specification – a checklist that the LLM must satisfy (exact filenames, function signatures, comments, build‑script).
Post‑generation checklist – a short “what to verify” list that you (or the LLM) can run after the code is emitted.
You just need to feed the whole block to the LLM once. The model will output every source file, the README, a CMakeLists.txt (or a Visual‑Studio solution) and a tiny “how‑to‑run” section. After you compile, you’re ready to launch the overlay.

📦 1️⃣ High‑level brief (copy this exactly)
[BEGIN PROMPT]

You are a senior software engineer. Create a **complete, build‑able project** that implements a **real‑time “best‑move” overlay for a Tetris‑style game** using **only visual information** (no memory reads). The overlay must run on Windows, finish the whole frame‑to‑ghost pipeline in **≤ 5 ms** on a typical modern laptop, and be easy to compile with a single command.

**Constraints**
* Language: **C++17** (the fastest option, no garbage collector).  
* Use the following third‑party libraries (all available via vcpkg or NuGet):  
  - **DXGI / Direct3D 11** for screen capture (Desktop Duplication).  
  - **OpenCV 4.x** for image processing (HSV, threshold, resize).  
  - **Direct2D 1.1** for a transparent, click‑through overlay window.  
  - **Optional**: **ONNX Runtime** (C++ API) if a CNN model is chosen.  
* Build system: **CMake 3.15+** (generate VS2022 solution or a Makefile).  
* All source files must reside under a top‑level folder `tetris_overlay/`.  
* Provide a **single‑step** `README.md` with build and run instructions.  
* The code must be **well‑commented** and each logical component should be isolated in its own file (see the file‑spec list below).  
* Do **not** include any proprietary/closed‑source code; rely only on the libraries listed.  
* Do not use any platform‑specific tricks that require admin rights – the program must run as a normal user.  

**What you have to output**
1. A `CMakeLists.txt` that builds the whole project.  
2. All source/header files listed in the **File Specification** (see section 2).  
3. A short `README.md` that explains:
   * How to install the required 3rd‑party libraries with **vcpkg** (one‑line commands).  
   * How to run `cmake -S . -B build && cmake --build build` (or open the generated VS solution).  
   * How to calibrate the board ROI (run the calibration utility, click TL/BR).  
   * Expected runtime behaviour (ghost piece follows the AI).  
4. A **tiny sample JSON** file `calibration.json` (placeholder values).  
5. **No binary data** (e.g., do not embed a trained CNN – if you use a CNN, just provide a stub that loads `tetris_cnn.onnx` and returns a dummy prediction).  

**Testing**
Add a small **self‑test** in `src/main.cpp` that, after building, runs the pipeline for 200 ms and prints the measured latency for each stage (capture, board extraction, prediction, overlay draw). Use `std::chrono::high_resolution_clock`.  

**Error handling**
All public functions must return a `bool` indicating success and write an error message to `std::cerr` if something fails (e.g., DXGI acquisition error, OpenCV conversion failure).  

**Style**
* Use `#pragma once` in headers.  
* Keep class/struct names short but expressive (`FrameGrabber`, `BoardExtractor`, `HeuristicEngine`, `OverlayRenderer`).  
* All public methods should be documented with a brief Doxygen‑style comment (`///`).  
* Do not use `using namespace std;` in headers.  

**File Specification** (see next section).  
Do not add any extra files beyond what is listed.  

[END PROMPT]
Copy the whole block inside the triple‑backticks (```) and paste it into your LLM. It will understand the “You must output X, Y, Z” instruction and produce the required artifacts automatically.

📂 2️⃣ File Specification – what the LLM must emit
Below is the exact list of files, their relative paths, and the required API surface. The LLM should copy‑paste the code for each file verbatim (including the header guards, includes, and Doxygen comments).

Path	Description	Must contain
CMakeLists.txt	Top‑level CMake script	Minimum version 3.15, project(TetrisOverlay), add_executable(tetris_overlay src/main.cpp src/frame_grabber.cpp src/board_extractor.cpp src/heuristic_engine.cpp src/overlay_renderer.cpp src/calibrate.cpp), find_package(OpenCV REQUIRED), target_link_libraries(tetris_overlay PRIVATE opengl32 d3d11 dxgi d2d1 d2d1_1), optional onnxruntime.
README.md	Build & run guide	Sections: Prerequisites, Install dependencies (vcpkg command), Build, Run, Calibration, Performance test.
calibration.json	Placeholder ROI file	{ "x": 150, "y": 100, "w": 300, "h": 600 } (user can edit).
src/main.cpp	Entry point, orchestrates all components, runs a 200 ms benchmark, starts overlay loop.	int main() creates objects: FrameGrabber, BoardExtractor, HeuristicEngine, OverlayRenderer. Calls runBenchmark() and then overlayRenderer.start(); – non‑blocking overlay loop runs until ESC pressed.
src/frame_grabber.h	Class that wraps DXGI Desktop Duplication.	cpp\nclass FrameGrabber {\npublic:\n FrameGrabber();\n bool grab(cv::Mat& out);\n ~FrameGrabber();\nprivate:\n // COM pointers (IDXGIFactory2, IDXGIOutputDuplication, ID3D11Device, ID3D11DeviceContext, ID3D11Texture2D)\n};\n
src/frame_grabber.cpp	Implementation of FrameGrabber::grab.	Use IDXGIOutputDuplication::AcquireNextFrame, copy to staging texture, map, construct a cv::Mat header that points to the mapped data, unmap and ReleaseFrame.
src/board_extractor.h	Convert the captured frame to a 20×10 binary matrix.	cpp\nclass BoardExtractor {\npublic:\n explicit BoardExtractor(const cv::Rect& roi);\n cv::Mat extract(const cv::Mat& frame) const; ///< returns CV_8U 20×10 matrix (0/1)\nprivate:\n cv::Rect m_roi; int m_cellW, m_cellH;\n};\n
src/board_extractor.cpp	Implements ROI crop, HSV conversion, inRange, morphological closing, resize to 10 × 20, threshold to 0/1.	
src/heuristic_engine.h	Hand‑crafted weighted‑sum engine and optional CNN stub.	cpp\nstruct Prediction { int rotation; int column; float score; std::string piece_type; };\n\nclass HeuristicEngine {\npublic:\n HeuristicEngine(); // loads optional CNN (if onnxruntime available)\n Prediction evaluate(const cv::Mat& board, const std::string& curPiece);\nprivate:\n // internal tetromino shape tables (uint16_t masks)\n // optional: Ort::Session m_onnxSession;\n};\n
src/heuristic_engine.cpp	Implements evaluate:\n*Enumerate every legal placement (≈ 34 combos) for the given piece, simulate drop, clear lines, compute weighted sum (lines, holes, aggregate height, bumpiness, well depth). Return best (rot, col, score, piece_type). If the optional ONNX model is present, call it instead of the heuristic.	
src/overlay_renderer.h	Transparent, click‑through overlay using Direct2D.	cpp\nclass OverlayRenderer {\npublic:\n OverlayRenderer(int width, int height, int cellSize);\n ~OverlayRenderer();\n void drawGhost(const Prediction& pred);\n void start(); // enters message loop, draws every frame until ESC\nprivate:\n HWND m_hwnd;\n Microsoft::WRL::ComPtr<ID2D1Factory1> m_factory;\n Microsoft::WRL::ComPtr<ID2D1HwndRenderTarget> m_rt;\n Microsoft::WRL::ComPtr<ID2D1SolidColorBrush> m_brush;\n int m_cellSize;\n};\n
src/overlay_renderer.cpp	Implements window creation (CreateWindowExW with `WS_EX_LAYERED	WS_EX_TRANSPARENT
src/calibrate.cpp	Small utility that loads calibration.json, opens a window showing the current screen (use FrameGrabber), lets the user click top‑left and bottom‑right corners (Win32 mouse hook), writes the ROI back to calibration.json.	
src/calibrate.h	Header for the calibration helper (optional – you may embed everything in calibrate.cpp).	
src/utils.h (optional)	Small helper functions (float lerp(float a,float b,float t), bool fileExists(const std::string&)).	
All .cpp files must include the matching .h file first (#include "frame_grabber.h" etc.).

✅ 3️⃣ Post‑generation checklist (run after the LLM finishes)
Create a vcpkg environment (if you don’t already have one):

git clone https://github.com/microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.bat
./vcpkg/vcpkg integrate install
./vcpkg/vcpkg install opencv[core]:x64-windows d3d11 dxgi direct2d onnxruntime
Generate the build files:

cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=[path_to_vcpkg]/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
If you use Visual Studio, open the generated .sln and build the tetris_overlay project.

Run the calibration utility (first run):

build\Release\calibrate.exe
Click the top‑left then bottom‑right corner of the Tetris board. The file calibration.json is written.

Run the overlay:

build\Release\tetris_overlay.exe
You should see a semi‑transparent yellow ghost piece following the AI’s suggestion. Press Esc to quit.

Verify latency – the program prints something like:

Capture   : 0.94 ms
Board proc: 0.38 ms
Predict   : 0.71 ms
Overlay   : 0.31 ms
Total per frame: 2.34 ms (≈ 430 FPS)
If any stage exceeds 5 ms, look at the corresponding implementation file (e.g., make sure the DXGI duplication is using AcquireNextFrame(0, …) with a timeout of zero).

Optional – CNN path: drop a valid ONNX model named tetris_cnn.onnx in the executable folder, rebuild (cmake --build build), and the HeuristicEngine will automatically use the model instead of the handcrafted heuristic.

Run unit tests (if you added any) – they are compiled into the same binary; the benchmark in main.cpp already acts as a sanity check.

If all the above steps succeed, you now have a production‑ready low‑latency overlay that can be used to train yourself on any Tetris‑style game without any memory hacks.

🎉 How to give this to your own LLM
Copy the entire block from section 1 (the “BEGIN PROMPT” … “END PROMPT” part).
Paste it into the prompt box of your LLM (or feed it via API).
Make sure you request “all output in a single response” or enable streaming if the model splits the answer.
The LLM will return all files in the order you asked for, each wrapped in triple‑backticks (```cpp) so you can easily extract them to the file system.
That’s it – the LLM will do all the “leg work” for you, and you’ll have a lightning‑fast Tetris‑prediction overlay ready to compile and run. Good luck, and happy stacking! 🚀