#include "logger.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    LOG_INFO("rotation_test", "Testing log rotation with 10K line limit");
    
    // Write enough lines to trigger rotation (let's do 100 to test quickly)
    for (int i = 0; i < 100; ++i) {
        LOG_INFO("rotation_test", "Test line " + std::to_string(i + 1));
        
        // Small delay to make timestamps different
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    LOG_SUCCESS("rotation_test", "Rotation test completed");
    std::cout << "Rotation test completed. Check for rotated log files." << std::endl;
    std::cout << "Run this test multiple times to see cleanup in action." << std::endl;
    
    return 0;
}
