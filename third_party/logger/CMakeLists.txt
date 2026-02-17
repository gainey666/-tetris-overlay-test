cmake_minimum_required(VERSION 3.20)
project(LoggerTest)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the logger library (header-only)
add_library(logger INTERFACE)
target_include_directories(logger INTERFACE ${CMAKE_CURRENT_SOURCE_DIR})

# Test executable
add_executable(test_logger test_logger.cpp)
target_link_libraries(test_logger logger)

# Rotation test executable  
add_executable(test_rotation test_rotation.cpp)
target_link_libraries(test_rotation logger)

# Enhanced logging test executable
add_executable(test_enhanced_logging test_enhanced_logging.cpp)
target_link_libraries(test_enhanced_logging logger)
