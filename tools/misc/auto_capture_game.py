import mss
import time
from PIL import Image
import os

def auto_capture_game():
    """Capture game screenshots every 30 seconds for 5 minutes"""
    
    # Create screenshots directory
    os.makedirs("game_screenshots", exist_ok=True)
    
    # Monitor 3 coordinates (your main monitor)
    monitor_left = 0
    monitor_top = 0
    monitor_width = 1920
    monitor_height = 1080
    
    # Centered game area (1024x768 centered in 1920x1080)
    game_left = monitor_left + (monitor_width - 1024) // 2  # 448
    game_top = monitor_top + (monitor_height - 768) // 2   # 156
    game_width = 1024
    game_height = 768
    
    print(f"Auto-capturing game area: ({game_left}, {game_top}, {game_width}x{game_height})")
    print("Starting 5-minute capture session (10 screenshots, 30 seconds apart)")
    print("Press Ctrl+C to stop early")
    print()
    
    with mss.mss() as sct:
        region = {"left": game_left, "top": game_top, "width": game_width, "height": game_height}
        
        for i in range(10):  # 10 screenshots = 5 minutes
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"game_screenshots/game_{timestamp}_{i+1:02d}.png"
            
            try:
                shot = sct.grab(region)
                screenshot = Image.frombytes("RGB", shot.size, shot.rgb)
                screenshot.save(filename)
                file_size = os.path.getsize(filename)
                print(f"Screenshot {i+1}/10 saved: {filename} ({file_size} bytes)")
                
                if i < 9:  # Don't sleep after last screenshot
                    print("Waiting 30 seconds...")
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\nCapture stopped by user")
                break
            except Exception as e:
                print(f"Error capturing screenshot {i+1}: {e}")
                continue
    
    print(f"\nCapture complete! Screenshots saved in 'game_screenshots/' directory")
    print("You can now analyze the game board positions across all screenshots")

if __name__ == "__main__":
    auto_capture_game()
