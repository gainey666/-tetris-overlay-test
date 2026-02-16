#!/usr/bin/env python3
"""Quick calibration to get overlay running"""

import json

# Create a basic calibration that works for most Tetris games
basic_calibration = {
    "left_board": [100, 200, 300, 600],
    "right_board": [500, 200, 300, 600],
    "next_queue_left": [450, 100, 50, 200],
    "next_queue_right": [400, 100, 50, 200],
    "score": [300, 50, 200, 50],
    "wins": [300, 10, 200, 30],
    "timer": [250, 10, 100, 30],
    # Add required shared UI ROIs
    "left_score": [300, 50, 200, 50],
    "right_score": [550, 50, 200, 50],
    "left_wins": [300, 10, 200, 30],
    "right_wins": [550, 10, 200, 30],
    "global_timer": [400, 10, 100, 30]
}

# Save to calibration.json
with open("calibration.json", "w") as f:
    json.dump(basic_calibration, f, indent=2)

print("✅ Quick calibration created with all required ROIs!")
print("🎯 Now run: python run_overlay_core.py")
