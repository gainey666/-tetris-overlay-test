// Example of what the enhanced logging will produce
#include "logger.hpp"
#include <iostream>

bool validate_piece_position(int x, int y, std::string piece_type) {
    // This will log: 🟢 [2026-02-16 19:15:30.123] validate_piece_position(line 4) in capture.cpp: INPUT(x=10, y=5, piece_type="T") -> EXPECTED(valid_position) -> ACTUAL(true) 🟢 SUCCESS
    
    LOG_FUNCTION_ENTER("validate_piece_position", 4, "capture.cpp", 
                      "INPUT(x=" + std::to_string(x) + ", y=" + std::to_string(y) + ", piece_type=\"" + piece_type + "\")");
    
    bool expected_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    bool actual_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    
    if (actual_result == expected_result) {
        LOG_FUNCTION_SUCCESS("validate_piece_position", 4, "capture.cpp",
                           "EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ")");
        return actual_result;
    } else {
        LOG_FUNCTION_ERROR("validate_piece_position", 4, "capture.cpp",
                          "EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ") 🚨 RED FLAG");
        return actual_result;
    }
}

int calculate_score(int lines_cleared, int level) {
    // This will log: 🟡 [2026-02-16 19:15:31.456] calculate_score(line 15) in game_logic.cpp: INPUT(lines_cleared=4, level=3) -> EXPECTED(score>0) -> ACTUAL(1200) 🟡 WARNING
    
    LOG_FUNCTION_ENTER("calculate_score", 15, "game_logic.cpp", 
                      "INPUT(lines_cleared=" + std::to_string(lines_cleared) + ", level=" + std::to_string(level) + ")");
    
    int base_score = lines_cleared * 100;
    int level_multiplier = level * 4;
    int actual_score = base_score * level_multiplier;
    
    if (lines_cleared == 0) {
        LOG_FUNCTION_WARNING("calculate_score", 15, "game_logic.cpp",
                            "EXPECTED(lines_cleared>0) -> ACTUAL(" + std::to_string(lines_cleared) + ") 🟡 WARNING - No lines cleared");
    } else if (actual_score > 10000) {
        LOG_FUNCTION_SUCCESS("calculate_score", 15, "game_logic.cpp",
                             "EXPECTED(score>0) -> ACTUAL(" + std::to_string(actual_score) + ") 🟢 EXCELLENT");
    } else {
        LOG_FUNCTION_INFO("calculate_score", 15, "game_logic.cpp",
                         "EXPECTED(score>0) -> ACTUAL(" + std::to_string(actual_score) + ") ⚪ NORMAL");
    }
    
    return actual_score;
}

void process_game_state() {
    // This will log: ⚪ [2026-02-16 19:15:32.789] process_game_state(line 25) in main.cpp: INPUT() -> EXPECTED(state_update) -> ACTUAL(processing) ⚪ INFO
    
    LOG_FUNCTION_ENTER("process_game_state", 25, "main.cpp", "INPUT()");
    
    try {
        // Game processing logic here
        LOG_FUNCTION_INFO("process_game_state", 25, "main.cpp", 
                         "EXPECTED(state_update) -> ACTUAL(processing) ⚪ INFO");
    } catch (const std::exception& e) {
        LOG_FUNCTION_ERROR("process_game_state", 25, "main.cpp",
                           "EXPECTED(state_update) -> ACTUAL(exception: " + std::string(e.what()) + ") 🔴 CRITICAL ERROR");
    }
}

int main() {
    std::cout << "Enhanced Logging Example:\n\n";
    
    // Example 1: Success case
    bool valid = validate_piece_position(5, 10, "T");
    
    // Example 2: Warning case  
    int score = calculate_score(0, 1);
    
    // Example 3: Info case
    process_game_state();
    
    std::cout << "Check the console and tetris_overlay.log for detailed function tracking!\n";
    return 0;
}
