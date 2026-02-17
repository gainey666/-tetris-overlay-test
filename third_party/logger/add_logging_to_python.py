#!/usr/bin/env python3
"""
Utility to add logger bridge imports and basic logging to Python files.
This script scans Python files and adds logging calls to key methods.
"""

import os
import re
from pathlib import Path
from typing import List, Set

# Files to skip (already processed or special cases)
SKIP_FILES = {
    '__pycache__', '.git', 'build', 'dist', '.venv',
    'logger_bridge.py', 'test_logger_bridge.py'
}

# Patterns for common method definitions
METHOD_PATTERNS = [
    r'def __init__\(self',
    r'def start\(self',
    r'def stop\(self', 
    r'def handle\(self',
    r'def run\(self',
    r'def main\(',
    r'class \w+\(',
]

def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    if any(skip in str(filepath) for skip in SKIP_FILES):
        return False
    
    if not filepath.suffix == '.py':
        return False
        
    # Skip if already has logger bridge import
    try:
        content = filepath.read_text(encoding='utf-8')
        if 'logger_bridge' in content:
            return False
    except:
        return False
        
    return True

def add_logger_import(content: str) -> str:
    """Add logger bridge import after existing imports."""
    # Find the last import statement
    lines = content.split('\n')
    import_end = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            import_end = i
    
    if import_end >= 0:
        # Insert after the last import
        lines.insert(import_end + 1, '')
        lines.insert(import_end + 2, '# Import our logger bridge')
        lines.insert(import_end + 3, 'try:')
        lines.insert(import_end + 4, '    import logger_bridge as log')
        lines.insert(import_end + 5, '    LOGGER_AVAILABLE = True')
        lines.insert(import_end + 6, 'except ImportError:')
        lines.insert(import_end + 7, '    LOGGER_AVAILABLE = False')
        lines.insert(import_end + 8, '')
    else:
        # No imports found, add at top
        lines.insert(0, '# Import our logger bridge')
        lines.insert(1, 'try:')
        lines.insert(2, '    import logger_bridge as log')
        lines.insert(3, '    LOGGER_AVAILABLE = True')
        lines.insert(4, 'except ImportError:')
        lines.insert(5, '    LOGGER_AVAILABLE = False')
        lines.insert(6, '')
    
    return '\n'.join(lines)

def add_logging_calls(content: str, filepath: Path) -> str:
    """Add logging calls to key methods."""
    lines = content.split('\n')
    result_lines = []
    classname = ''
    
    for i, line in enumerate(lines):
        result_lines.append(line)
        
        # Track class name for logging context
        class_match = re.match(r'^\s*class\s+(\w+)', line)
        if class_match:
            classname = class_match.group(1)
            continue
            
        # Add logging to key methods
        for pattern in METHOD_PATTERNS:
            if re.search(pattern, line):
                # Get method name
                method_match = re.search(r'def\s+(\w+)', line)
                if method_match:
                    method_name = method_match.group(1)
                    
                    # Add logging after the method definition
                    # Look for the next non-empty line that's not a docstring
                    j = i + 1
                    while j < len(lines) and (lines[j].strip() == '' or 
                                             lines[j].strip().startswith('"""') or
                                             lines[j].strip().startswith("'''")):
                        j += 1
                    
                    if j < len(lines):
                        # Determine context for logging
                        context = classname if classname else method_name
                        
                        # Add appropriate logging call
                        if method_name == '__init__':
                            log_call = f'        if LOGGER_AVAILABLE:\n            log.log_info("{context}", "Initialized")'
                        elif method_name in ['start', 'run', 'main']:
                            log_call = f'        if LOGGER_AVAILABLE:\n            log.log_info("{context}", "Starting")'
                        elif method_name == 'stop':
                            log_call = f'        if LOGGER_AVAILABLE:\n            log.log_info("{context}", "Stopping")'
                        elif method_name == 'handle':
                            log_call = f'        if LOGGER_AVAILABLE:\n            log.log_info("{context}", "Handling request")'
                        else:
                            log_call = f'        if LOGGER_AVAILABLE:\n            log.log_info("{context}", "Method {method_name} called")'
                        
                        # Insert the logging call
                        if j < len(result_lines):
                            result_lines.insert(j, log_call)
                        break
    
    return '\n'.join(result_lines)

def process_file(filepath: Path) -> bool:
    """Process a single Python file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Add import
        if 'logger_bridge' not in content:
            content = add_logger_import(content)
            
        # Add logging calls
        content = add_logging_calls(content, filepath)
        
        # Write back
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Processed: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to process Python files."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src directory not found")
        return
    
    python_files = list(src_dir.rglob("*.py"))
    processable_files = [f for f in python_files if should_process_file(f)]
    
    print(f"📁 Found {len(python_files)} Python files")
    print(f"📝 Will process {len(processable_files)} files")
    
    processed = 0
    for filepath in processable_files:
        if process_file(filepath):
            processed += 1
    
    print(f"✨ Successfully processed {processed}/{len(processable_files)} files")

if __name__ == "__main__":
    main()
