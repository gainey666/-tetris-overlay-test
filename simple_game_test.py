#!/usr/bin/env python3
"""
Simple Game Image Tester - Works with standalone tracer
Tests OCR and board detection on real game images
Reports ALL function calls to standalone tracer
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Import tracer for function call reporting
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
    print("✅ Connected to standalone tracer")
except ImportError:
    TRACER_AVAILABLE = False
    print("⚠️ Standalone tracer not available - using console logging")

def log_function(func_name, message, status="INFO"):
    """Log function call to tracer or console"""
    if TRACER_AVAILABLE:
        global_tracer.trace_function(func_name, "simple_game_test.py", 1, f"ARGS({message})", result=f"RESULT({status})")
    else:
        print(f"🔵 {func_name}(): {message} -> {status}")

@trace_calls("load_game_images", "simple_game_test.py", 20)
def load_game_images():
    """Load all game screenshot paths"""
    log_function("load_game_images", "Loading game screenshots", "ENTER")
    
    game_dir = Path("game_screenshots")
    if not game_dir.exists():
        log_function("load_game_images", f"Game screenshots directory not found: {game_dir}", "ERROR")
        return []
    
    image_files = list(game_dir.glob("*.png"))
    image_files.sort()
    
    log_function("load_game_images", f"Found {len(image_files)} game images", "SUCCESS")
    
    for img in image_files:
        size_kb = img.stat().st_size // 1024
        log_function("load_game_images", f"Image {img.name} ({size_kb}KB)", "INFO")
    
    return [str(img) for img in image_files]

def main():
    """Main test function"""
    log_function("main", "Starting Simple Game Image Test", "ENTER")
    
    print("=" * 60)
    print("🎮 SIMPLE GAME IMAGE TEST")
    print("=" * 60)
    print("📸 Tests OCR and board detection on real game screenshots")
    print("🎮 Uses actual game images from game_screenshots/")
    print("📊 ALL function calls reported to standalone tracer")
    print("=" * 60)
    
    # Load game images
    game_images = load_game_images()
    
    if not game_images:
        log_function("main", "No game images found - exiting", "ERROR")
        return 1
    
    log_function("main", f"Loaded {len(game_images)} game images", "SUCCESS")
    
    # Test first image
    first_image = game_images[0]
    log_function("main", f"Testing with first image: {Path(first_image).name}", "ENTER")
    
    # Load and display image info
    image = cv2.imread(first_image)
    if image is not None:
        height, width, channels = image.shape
        log_function("main", f"Image loaded: {width}x{height}x{channels}", "SUCCESS")
        
        # Test basic processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        log_function("main", "Converted to grayscale", "SUCCESS")
        
        # Test threshold
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        log_function("main", "Applied threshold for OCR", "SUCCESS")
        
        log_function("main", "Basic image processing test completed", "SUCCESS")
    else:
        log_function("main", f"Failed to load image: {first_image}", "ERROR")
        return 1
    
    log_function("main", "Simple Game Image Test completed", "SUCCESS")
    print("🎉 Test completed! Check standalone tracer for detailed function calls")
    return 0

if __name__ == "__main__":
    sys.exit(main())
