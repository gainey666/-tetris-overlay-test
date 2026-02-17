#!/usr/bin/env python3
"""
Clean up broken tracer decorators from original overlay files
Removes @trace_calls decorators that are causing syntax errors
"""

import re
from pathlib import Path

def clean_file(file_path):
    """Remove broken tracer decorators from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove @trace_calls decorators
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines with @trace_calls decorators
            if re.match(r'^\s*@trace_calls\s*\(', line):
                continue
            cleaned_lines.append(line)
        
        # Write back cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
        
        print(f"✅ Cleaned {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def main():
    """Clean all overlay files"""
    print("🧹 Cleaning broken tracer decorators from overlay files...")
    
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src directory not found")
        return
    
    # Files that need cleaning
    files_to_clean = [
        "src/tetris_overlay/core/overlay.py",
        "src/tetris_overlay/ui/wizard.py", 
        "src/tetris_overlay/ui/settings_dialog.py",
        "src/tetris_overlay/core/wgc_capture.py",
        "src/tetris_overlay/utils/logger.py",
        "src/tetris_overlay/__main__.py",
        "src/window_filter_old.py"
    ]
    
    cleaned = 0
    for file_path in files_to_clean:
        full_path = Path(file_path)
        if full_path.exists():
            if clean_file(full_path):
                cleaned += 1
    
    print(f"✅ Successfully cleaned {cleaned}/{len(files_to_clean)} files")
    print("🎮 Original overlay system should now work!")

if __name__ == "__main__":
    main()
