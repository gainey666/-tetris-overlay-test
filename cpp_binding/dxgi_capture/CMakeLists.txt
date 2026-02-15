cmake_minimum_required(VERSION 3.15)
project(dxgi_capture)

include(FetchContent)
FetchContent_Declare(
    pybind11
    URL https://github.com/pybind/pybind11/archive/refs/tags/v2.11.1.tar.gz
)
FetchContent_MakeAvailable(pybind11)

find_package(OpenCV REQUIRED)

pybind11_add_module(dxgi_capture
    pybind_module.cpp
    dxgi_frame_grabber.cpp
)

set_target_properties(dxgi_capture PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)

target_link_libraries(dxgi_capture PRIVATE
    d3d11.lib
    dxgi.lib
    dxguid.lib
    windowsapp.lib
    ${OpenCV_LIBS}
)

target_include_directories(dxgi_capture PRIVATE ${OpenCV_INCLUDE_DIRS})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DWIN32_LEAN_AND_MEAN -DNOMINMAX")
