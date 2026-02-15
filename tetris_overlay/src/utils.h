#pragma once
#include <chrono>
#include <iostream>

/** Simple RAII timer that prints elapsed time when it goes out of scope. */
class ScopedTimer {
public:
    explicit ScopedTimer(const char* name) : m_name(name), m_start(std::chrono::high_resolution_clock::now()) {}
    ~ScopedTimer() {
        auto end = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(end - m_start).count();
        std::cout << "[" << m_name << "] " << ms << " ms\n";
    }
private:
    const char* m_name;
    std::chrono::high_resolution_clock::time_point m_start;
};
