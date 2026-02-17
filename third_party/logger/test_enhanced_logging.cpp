#include "logger.hpp"
#include <iostream>
#include <string>

bool validate_piece_position(int x, int y, std::string piece_type) {
    // 🟢 [2026-02-16 19:15:30.123] 🟢 validate_piece_position(line 8) in test_enhanced.cpp: INPUT(x=10, y=5, piece_type="T") -> ENTER 🔵 function_started
    
    LOG_FUNCTION_ENTER("INPUT(x=" + std::to_string(x) + ", y=" + std::to_string(y) + ", piece_type=\"" + piece_type + "\")");
    
    bool expected_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    bool actual_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    
    if (actual_result == expected_result) {
        // 🟢 [2026-02-16 19:15:30.124] 🟢 validate_piece_position(line 8) in test_enhanced.cpp: EXPECTED(valid_position) -> ACTUAL(true) 🟢 SUCCESS
        LOG_FUNCTION_SUCCESS("EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ")");
        return actual_result;
    } else {
        // 🔴 [2026-02-16 19:15:30.124] 🔴 validate_piece_position(line 8) in test_enhanced.cpp: EXPECTED(valid_position) -> ACTUAL(false) 🔴 ERROR
        LOG_FUNCTION_ERROR("EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ") 🚨 RED FLAG");
        return actual_result;
    }
}

int calculate_score(int lines_cleared, int level) {
    // 🟡 [2026-02-16 19:15:31.456] 🟡 calculate_score(line 25) in test_enhanced.cpp: INPUT(lines_cleared=0, level=1) -> ENTER 🔵 function_started
    
    LOG_FUNCTION_ENTER("INPUT(lines_cleared=" + std::to_string(lines_cleared) + ", level=" + std::to_string(level) + ")");
    
    int base_score = lines_cleared * 100;
    int level_multiplier = level * 4;
    int actual_score = base_score * level_multiplier;
    
    if (lines_cleared == 0) {
        // 🟡 [2026-02-16 19:15:31.457] 🟡 calculate_score(line 25) in test_enhanced.cpp: EXPECTED(lines_cleared>0) -> ACTUAL(0) 🟡 WARNING
        LOG_FUNCTION_WARNING("EXPECTED(lines_cleared>0) -> ACTUAL(" + std::to_string(lines_cleared) + ") 🟡 WARNING - No lines cleared");
    } else if (actual_score > 10000) {
        // 🟢 [2026-02-16 19:15:31.457] 🟢 calculate_score(line 25) in test_enhanced.cpp: EXPECTED(score>0) -> ACTUAL(12000) 🟢 SUCCESS
        LOG_FUNCTION_SUCCESS("EXPECTED(score>0) -> ACTUAL(" + std::to_string(actual_score) + ") 🟢 EXCELLENT");
    } else {
        // ⚪ [2026-02-16 19:15:31.457] ⚪ calculate_score(line 25) in test_enhanced.cpp: EXPECTED(score>0) -> ACTUAL(400) ⚪ INFO
        LOG_FUNCTION_INFO("EXPECTED(score>0) -> ACTUAL(" + std::to_string(actual_score) + ") ⚪ NORMAL");
    }
    
    return actual_score;
}

void process_game_state() {
    // ⚪ [2026-02-16 19:15:32.789] ⚪ process_game_state(line 42) in test_enhanced.cpp: INPUT() -> ENTER 🔵 function_started
    
    LOG_FUNCTION_ENTER("INPUT()");
    
    try {
        // Game processing logic here
        // ⚪ [2026-02-16 19:15:32.790] ⚪ process_game_state(line 42) in test_enhanced.cpp: EXPECTED(state_update) -> ACTUAL(processing) ⚪ INFO
        LOG_FUNCTION_INFO("EXPECTED(state_update) -> ACTUAL(processing) ⚪ NORMAL OPERATION");
    } catch (const std::exception& e) {
        // 🔴 [2026-02-16 19:15:32.790] 🔴 process_game_state(line 42) in test_enhanced.cpp: EXPECTED(state_update) -> ACTUAL(exception: memory_error) 🔴 ERROR
        LOG_FUNCTION_ERROR("EXPECTED(state_update) -> ACTUAL(exception: " + std::string(e.what()) + ") 🔴 CRITICAL ERROR");
    }
}

void demonstrate_error_case() {
    // 🔴 [2026-02-16 19:15:33.111] 🔴 demonstrate_error_case(line 55) in test_enhanced.cpp: INPUT(data="invalid") -> ENTER 🔵 function_started
    
    LOG_FUNCTION_ENTER("INPUT(data=\"invalid\")");
    
    // Simulate an error condition
    bool data_valid = false;
    if (!data_valid) {
        // 🔴 [2026-02-16 19:15:33.112] 🔴 demonstrate_error_case(line 55) in test_enhanced.cpp: EXPECTED(valid_data) -> ACTUAL(invalid_data) 🔴 ERROR
        LOG_FUNCTION_ERROR("EXPECTED(valid_data) -> ACTUAL(invalid_data) 🔴 RED FLAG - Data validation failed");
        return;
    }
    
    LOG_FUNCTION_SUCCESS("EXPECTED(valid_data) -> ACTUAL(valid_data) 🟢 SUCCESS");
}

int main() {
    std::cout << "🚀 Enhanced Logging System Demonstration\n";
    std::cout << "📋 Check console output and tetris_overlay.log for detailed function tracking\n\n";
    
    // Example 1: Success case 🟢
    std::cout << "🟢 Testing success case...\n";
    bool valid = validate_piece_position(5, 10, "T");
    
    // Example 2: Warning case 🟡
    std::cout << "🟡 Testing warning case...\n";
    int score = calculate_score(0, 1);
    
    // Example 3: Info case ⚪
    std::cout << "⚪ Testing info case...\n";
    process_game_state();
    
    // Example 4: Error case 🔴
    std::cout << "🔴 Testing error case...\n";
    demonstrate_error_case();
    
    std::cout << "\n✨ Enhanced logging demonstration completed!\n";
    std::cout << "📊 Each function shows: function_name(line X) in file.ext: INPUT(values) -> EXPECTED(outcome) -> ACTUAL(result) 🎨STATUS\n";
    std::cout << "🎯 This is now the MANDATORY standard for ALL functions in the project!\n";
    
    return 0;
}
