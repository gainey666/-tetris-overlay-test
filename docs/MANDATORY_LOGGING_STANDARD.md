# 🚨 MANDATORY LOGGING STANDARD - Tetris Overlay Project

## 📋 **REQUIREMENT: EVERY Function Must Log**

**This is NOT optional - ALL functions must follow this logging standard exactly.**

---

## 🎯 **Required Log Format for EVERY Function**

### 📝 **Exact Format:**
```
[timestamp] 🎨function_name(line X) in filename.ext: INPUT(values) -> EXPECTED(outcome) -> ACTUAL(result) 🎨STATUS message
```

### 🎨 **Color-Coded Status Levels:**
- 🟢 **GREEN (SUCCESS)** = Passed with flying colors, exceeded expectations
- 🟡 **YELLOW (WARNING)** = Worked but with issues/caution
- 🔴 **RED (ERROR)** = Critical failure, RED FLAG problem  
- ⚪ **WHITE/GRAY (INFO)** = Normal operation, informational
- 🔵 **BLUE (DEBUG)** = Detailed debugging information

---

## 💻 **Implementation Examples**

### ✅ **C++ Functions - MANDATORY:**
```cpp
bool validate_piece_position(int x, int y, std::string piece_type) {
    // 🟢 [2026-02-16 19:15:30.123] 🟢 validate_piece_position(line 4) in capture.cpp: INPUT(x=10, y=5, piece_type="T") -> EXPECTED(valid_position) -> ACTUAL(true) 🟢 SUCCESS
    
    LOG_FUNCTION_ENTER("validate_piece_position", __LINE__, "capture.cpp", 
                      "INPUT(x=" + std::to_string(x) + ", y=" + std::to_string(y) + ", piece_type=\"" + piece_type + "\")");
    
    bool expected_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    bool actual_result = (x >= 0 && x < 10 && y >= 0 && y < 20);
    
    if (actual_result == expected_result) {
        LOG_FUNCTION_SUCCESS("validate_piece_position", __LINE__, "capture.cpp",
                           "EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ")");
        return actual_result;
    } else {
        LOG_FUNCTION_ERROR("validate_piece_position", __LINE__, "capture.cpp",
                          "EXPECTED(valid_position) -> ACTUAL(" + std::string(actual_result ? "true" : "false") + ") 🚨 RED FLAG");
        return actual_result;
    }
}
```

### 🐍 **Python Functions - MANDATORY:**
```python
def detect_ghost_piece(board, current_piece):
    # 🟢 [2026-02-16 19:15:35.678] 🟢 detect_ghost_piece(line 12) in ai_agent.py: INPUT(board=10x20_matrix, current_piece="T") -> EXPECTED(ghost_calculated) -> ACTUAL(ghost_at_x=5,y=18) 🟢 SUCCESS
    
    if LOGGER_AVAILABLE:
        log.log_function_enter("detect_ghost_piece", 12, "ai_agent.py", 
                              f"INPUT(board={len(board)}x{len(board[0])}_matrix, current_piece='{current_piece}')")
    
    try:
        ghost_pos = calculate_ghost_position(board, current_piece)
        if LOGGER_AVAILABLE:
            log.log_function_success("detect_ghost_piece", 12, "ai_agent.py",
                                    f"EXPECTED(ghost_calculated) -> ACTUAL(ghost_at_x={ghost_pos[0]},y={ghost_pos[1]})")
        return ghost_pos
    except Exception as e:
        if LOGGER_AVAILABLE:
            log.log_function_error("detect_ghost_piece", 12, "ai_agent.py",
                                  f"EXPECTED(ghost_calculated) -> ACTUAL(exception: {str(e)}) 🚨 RED FLAG")
        raise
```

---

## 📊 **Status Usage Guidelines**

### 🟢 **GREEN (SUCCESS) - Use When:**
- Function works perfectly
- Results exceed expectations  
- Performance is excellent
- All validations pass

### 🟡 **YELLOW (WARNING) - Use When:**
- Function works but with issues
- Performance is slower than expected
- Input values are concerning but handled
- Non-critical problems detected

### 🔴 **RED (ERROR) - Use When:**
- Function fails completely
- Critical errors occur
- Invalid data causes crashes
- RED FLAG issues that need immediate attention

### ⚪ **WHITE/GRAY (INFO) - Use When:**
- Normal operation logging
- State changes
- Configuration updates
- General information flow

### 🔵 **BLUE (DEBUG) - Use When:**
- Detailed troubleshooting needed
- Complex algorithm steps
- Data transformation details
- Performance analysis

---

## 🚨 **ENFORCEMENT POLICY**

### ✅ **What MUST Be Logged:**
1. **EVERY function entry** with inputs
2. **EVERY function exit** with results  
3. **EVERY error/exception** with details
4. **EVERY warning condition** with context
5. **EVERY performance issue** with metrics

### ❌ **NEVER Allowed:**
1. Functions without logging
2. Missing input values
3. Missing expected/actual outcomes
4. Missing line numbers
5. Missing file names

---

## 📋 **Code Review Checklist**

When reviewing code, verify:

- [ ] Every function has LOG_FUNCTION_ENTER
- [ ] Every function has LOG_FUNCTION_SUCCESS/ERROR/WARNING/INFO  
- [ ] All inputs are logged with values
- [ ] Expected vs Actual outcomes are shown
- [ ] Line numbers use `__LINE__` (C++) or actual line number (Python)
- [ ] File names are specified
- [ ] Status colors are appropriate
- [ ] Error conditions use RED status
- [ ] Success conditions use GREEN status

---

## 🔧 **Required Logger Macros/Functions**

### C++ Required Macros:
```cpp
LOG_FUNCTION_ENTER(name, line, file, inputs)
LOG_FUNCTION_SUCCESS(name, line, file, message)  
LOG_FUNCTION_WARNING(name, line, file, message)
LOG_FUNCTION_ERROR(name, line, file, message)
LOG_FUNCTION_INFO(name, line, file, message)
LOG_FUNCTION_DEBUG(name, line, file, message)
```

### Python Required Functions:
```python
log.log_function_enter(name, line, file, inputs)
log.log_function_success(name, line, file, message)
log.log_function_warning(name, line, file, message)  
log.log_function_error(name, line, file, message)
log.log_function_info(name, line, file, message)
log.log_function_debug(name, line, file, message)
```

---

## 📝 **Template for New Functions**

### C++ Template:
```cpp
return_type function_name(param_type param1, param_type param2) {
    LOG_FUNCTION_ENTER("function_name", __LINE__, "filename.cpp", 
                      "INPUT(param1=" + to_string(param1) + ", param2=" + to_string(param2) + ")");
    
    try {
        // Your function logic here
        return_type result = /* your calculation */;
        
        LOG_FUNCTION_SUCCESS("function_name", __LINE__, "filename.cpp",
                           "EXPECTED(expected_outcome) -> ACTUAL(" + to_string(result) + ")");
        return result;
    } catch (const exception& e) {
        LOG_FUNCTION_ERROR("function_name", __LINE__, "filename.cpp",
                          "EXPECTED(expected_outcome) -> ACTUAL(exception: " + string(e.what()) + ") 🚨 RED FLAG");
        throw;
    }
}
```

### Python Template:
```python
def function_name(param1, param2):
    if LOGGER_AVAILABLE:
        log.log_function_enter("function_name", 12, "filename.py", 
                              f"INPUT(param1={param1}, param2={param2})")
    
    try:
        # Your function logic here
        result = /* your calculation */
        
        if LOGGER_AVAILABLE:
            log.log_function_success("function_name", 12, "filename.py",
                                    f"EXPECTED(expected_outcome) -> ACTUAL({result})")
        return result
    except Exception as e:
        if LOGGER_AVAILABLE:
            log.log_function_error("function_name", 12, "filename.py",
                                  f"EXPECTED(expected_outcome) -> ACTUAL(exception: {str(e)}) 🚨 RED FLAG")
        raise
```

---

## ⚡ **Immediate Action Required**

**If you see code that does NOT follow this standard:**

1. 🛑 **STOP** - Do not merge/commit the code
2. 📝 **COMMENT** - Add review comments pointing out missing logging
3. 🔧 **FIX** - Require proper logging implementation
4. ✅ **VERIFY** - Ensure all functions comply before approval

---

## 🎯 **Project Success Depends on This**

This logging standard is **CRITICAL** for:
- 🔍 **Debugging complex issues**
- 📈 **Performance optimization**  
- 🛡️ **Quality assurance**
- 📊 **System monitoring**
- 🚀 **Future development**

**NO EXCEPTIONS - NO EXCUSES - EVERY FUNCTION MUST LOG!**

---

*This standard is effective immediately and applies to ALL code in the Tetris Overlay project.*
