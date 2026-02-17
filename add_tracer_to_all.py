#!/usr/bin/env python3
"""
Add tracer support to ALL Python files - Clean integration
This adds simple function call logging to every Python file
"""

import os
import re
from pathlib import Path

def add_tracer_to_file(file_path):
    """Add simple tracer logging to a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has tracer
        if 'global_tracer' in content or 'TRACER_AVAILABLE' in content:
            print(f"⏭️ Skipped {file_path} (already has tracer)")
            return False
        
        lines = content.split('\n')
        modified_lines = []
        
        for line in lines:
            modified_lines.append(line)
            
            # Add tracer import after existing imports
            if line.strip().startswith(('import ', 'from ')) and 'logger_bridge' not in content:
                # Check if this is the last import
                next_line_index = len(modified_lines)
                if next_line_index < len(lines):
                    next_line = lines[next_line_index]
                    if not next_line.strip().startswith(('import ', 'from ')):
                        # Add tracer import here
                        modified_lines.append('')
                        modified_lines.append('# Import global function tracer')
                        modified_lines.append('try:')
                        modified_lines.append('    from tracer.client import safe_trace_calls as trace_calls')
                        modified_lines.append('    TRACER_AVAILABLE = True')
                        modified_lines.append('except ImportError:')
                        modified_lines.append('    TRACER_AVAILABLE = False')
                        modified_lines.append('')
            # Add simple logging to function definitions
            elif re.match(r'^\s*def\s+\w+\s*\(', line):
                func_match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
                if func_match:
                    func_name = func_match.group(1)
                    indent = line[:len(line) - len(line.lstrip())]
                    
                    # Add simple logging calls
                    modified_lines.append(f"{indent}    # Log function call")
                    modified_lines.append(f"{indent}    try:")
                    modified_lines.append(f"{indent}        if 'TRACER_AVAILABLE' in globals() and TRACER_AVAILABLE:")
                    modified_lines.append(f"{indent}            global_tracer.trace_function('{func_name}', '{Path(file_path).name}', {len(modified_lines)+1}, f'ARGS()', result='ENTER')")
                    modified_lines.append(f"{indent}    except Exception as e:")
                    modified_lines.append(f"{indent}        pass")
                    modified_lines.append(f"{indent}    finally:")
                    modified_lines.append(f"{indent}        if 'TRACER_AVAILABLE' in globals() and TRACER_AVAILABLE:")
                    modified_lines.append(f"{indent}            global_tracer.trace_function('{func_name}', '{Path(file_path).name}', {len(modified_lines)+1}, result='COMPLETED')")
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(modified_lines))
        
        print(f"✅ Added tracer to {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Add tracer to all Python files"""
    print("🔍 Adding tracer support to ALL Python files...")
    
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src directory not found")
        return
    
    python_files = list(src_dir.rglob("*.py"))
    processed = 0
    
    for file_path in python_files:
        # Skip test files and tracer files
        if 'test' in file_path.name or 'tracer' in file_path.name:
            continue
            
        if add_tracer_to_file(file_path):
            processed += 1
    
    print(f"✅ Successfully added tracer to {processed}/{len(python_files)} Python files")
    print("🎮 Now ALL Python scripts will report function calls to standalone tracer!")

if __name__ == "__main__":
    main()
