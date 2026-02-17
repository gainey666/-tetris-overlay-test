cmake_minimum_required(VERSION 3.20)
project(TetrisCapture)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable C++/WinRT
set(CMAKE_VS_WINRT_BY_DEFAULT TRUE)

# Add the logger library (header-only)
add_library(logger INTERFACE)
target_include_directories(logger INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/logger)

# Add the capture library
add_library(capture_cpp SHARED
    capture.cpp
    capture.h
)

# Link libraries
target_link_libraries(capture_cpp
    logger
    d3d11
    dxgi
    windowsapp
)

# Set output directory
set_target_properties(capture_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
)
