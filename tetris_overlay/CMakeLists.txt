cmake_minimum_required(VERSION 3.15)

project(TetrisOverlay LANGUAGES CXX)

# -------------------------------------------------
# 0️⃣ Tell CMake to use the vcpkg toolchain (adjust path if needed)
# -------------------------------------------------
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/../vcpkg/scripts/buildsystems/vcpkg.cmake"
    CACHE STRING "Vcpkg toolchain file")

# -------------------------------------------------
# 1️⃣ C++ standard
# -------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------------------------------
# 2️⃣ Packages - try vcpkg first, then fallback to system/installed
# -------------------------------------------------
find_package(OpenCV QUIET)
if(NOT OpenCV_FOUND)
    # Try to find OpenCV in common locations
    set(OpenCV_DIR "" CACHE PATH "OpenCV directory")
    find_package(OpenCV REQUIRED)
endif()

find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    # nlohmann-json is header-only, we can include it directly
    set(nlohmann_json_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/third_party")
endif()

# DirectX and Direct2D are from Windows SDK
find_package(DirectX QUIET COMPONENTS D3D11 DXGI)
find_package(Direct2D QUIET)

# Optional ONNX Runtime
find_package(ONNXRuntime QUIET)

# -------------------------------------------------
# 3️⃣ Source files
# -------------------------------------------------
set(SRC
    src/main.cpp
    src/frame_grabber.cpp
    src/board_extractor.cpp
    src/heuristic_engine.cpp
    src/overlay_renderer.cpp
    src/calibrate.cpp
)

add_executable(tetris_overlay ${SRC})

# -------------------------------------------------
# 4️⃣ Include directories
# -------------------------------------------------
target_include_directories(tetris_overlay PRIVATE
    ${OpenCV_INCLUDE_DIRS}
    ${nlohmann_json_INCLUDE_DIRS}
)

# Add DirectX/Direct2D includes if found
if(DirectX_FOUND)
    target_include_directories(tetris_overlay PRIVATE ${DirectX_INCLUDE_DIR})
endif()
if(Direct2D_FOUND)
    target_include_directories(tetris_overlay PRIVATE ${Direct2D_INCLUDE_DIR})
endif()

# -------------------------------------------------
# 5️⃣ Link libraries
# -------------------------------------------------
target_link_libraries(tetris_overlay PRIVATE
    ${OpenCV_LIBS}
    d3d11.lib
    dxgi.lib
    d2d1.lib
    d2d1_1.lib
    user32.lib
    gdi32.lib
)

# -------------------------------------------------
# 6️⃣ Optional ONNX Runtime
# -------------------------------------------------
if (ONNXRuntime_FOUND)
    message(STATUS "ONNX Runtime found – enabling CNN backend")
    target_compile_definitions(tetris_overlay PRIVATE USE_ONNX)
    target_link_libraries(tetris_overlay PRIVATE ${ONNXRuntime_LIBRARIES})
    target_include_directories(tetris_overlay PRIVATE ${ONNXRuntime_INCLUDE_DIRS})
endif()

# -------------------------------------------------
# 7️⃣ Post-build copy of runtime DLLs (OpenCV & ONNX)
# -------------------------------------------------
if(OpenCV_FOUND)
    add_custom_command(TARGET tetris_overlay POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE:opencv_world455.dll>"  # This may vary based on OpenCV version
            $<TARGET_FILE_DIR:tetris_overlay>
        COMMENT "Copy OpenCV DLL"
    )
endif()

if (ONNXRuntime_FOUND)
    add_custom_command(TARGET tetris_overlay POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${ONNXRuntime_DLL}
            $<TARGET_FILE_DIR:tetris_overlay>
        COMMENT "Copy ONNX Runtime DLL"
    )
endif()
