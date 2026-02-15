cmake_minimum_required(VERSION 3.15)
project(board_processor_cpp)

include(FetchContent)
FetchContent_Declare(
    pybind11
    URL https://github.com/pybind/pybind11/archive/refs/tags/v2.11.1.tar.gz
)
FetchContent_MakeAvailable(pybind11)

find_package(OpenCV REQUIRED)

pybind11_add_module(board_processor_cpp
    pybind_module.cpp
    board_processor.cpp
)

target_link_libraries(board_processor_cpp PRIVATE ${OpenCV_LIBRARIES})
