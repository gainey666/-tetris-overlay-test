cmake_minimum_required(VERSION 3.20)
project(tetris_overlay)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenCV REQUIRED)
find_package(PkgConfig REQUIRED)

# Add executable
add_executable(tetris_overlay 
    src/main.cpp
    src/agents/capture_agent.cpp
    src/agents/board_extractor_agent.cpp
    src/agents/piece_detector_agent.cpp
    src/agents/prediction_agent.cpp
    src/agents/overlay_renderer_agent.cpp
    src/orchestrator/orchestrator.cpp
)

# Link libraries
target_link_libraries(tetris_overlay 
    ${OpenCV_LIBS}
)

# Include directories
target_include_directories(tetris_overlay PRIVATE 
    src
    ${OpenCV_INCLUDE_DIRS}
)

# Set output directory
set_target_properties(tetris_overlay PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/Release
)
