#!/usr/bin/env python3
"""
Test script to validate tracer works
Run this while tracer server is running
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tracer.client import safe_trace_calls as trace_calls

@trace_calls("S")
def foo(x):
    time.sleep(0.05)
    return x * 2

@trace_calls("F") 
def bar():
    raise ValueError("boom!")

@trace_calls("W")
def warning_func():
    print("This is a warning test")

def main():
    print("🧪 Testing tracer functionality...")
    print("📊 Make sure tracer server is running on localhost:8765")
    print("")
    
    for i in range(5):
        result = foo(i)
        print(f"✅ foo({i}) = {result}")
    
    try:
        bar()
    except Exception as e:
        print(f"❌ bar() raised: {e}")
    
    warning_func()
    
    print("")
    print("🎉 Test completed!")
    print("📊 Check tracer window for function calls")
    print("⏡ Keeping script alive for 2 seconds to ensure messages sent...")
    time.sleep(2)

if __name__ == "__main__":
    main()
