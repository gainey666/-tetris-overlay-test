#include "logger.hpp"
#include <iostream>

int main() {
    LOG_INFO("main", "Starting logger test");
    LOG_SUCCESS("main", "Logger initialized successfully");
    LOG_WARN("main", "This is a warning message");
    LOG_FAIL("main", "This is a failure message");
    
    std::cout << "Logger test completed. Check console and log file." << std::endl;
    return 0;
}
