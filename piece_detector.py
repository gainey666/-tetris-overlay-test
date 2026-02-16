"""Piece detection from next queue images."""

import cv2
import numpy as np
from typing import Optional, List
import logging

from next_queue_capture import capture_next_queue

log = logging.getLogger(__name__)

# Simple piece templates (for basic detection)
# These are approximate color ranges for each piece type
PIECE_TEMPLATES = {
    "I": {"avg_color": [100, 100, 255], "shape": "tall"},
    "O": {"avg_color": [255, 255, 100], "shape": "square"},
    "T": {"avg_color": [200, 100, 200], "shape": "t-shape"},
    "S": {"avg_color": [100, 255, 100], "shape": "z-shape"},
    "Z": {"avg_color": [255, 100, 100], "shape": "z-shape"},
    "J": {"avg_color": [100, 100, 200], "shape": "l-shape"},
    "L": {"avg_color": [200, 200, 100], "shape": "l-shape"},
}

def detect_piece_from_image(image) -> Optional[str]:
    """Detect piece type from a PIL image using simple color analysis."""
    try:
        # Convert PIL to numpy array (OpenCV format)
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if img_array.shape[2] == 3:  # RGB
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = img_array
        
        # Get average color
        avg_color = np.mean(img_bgr, axis=(0, 1))
        
        # Simple shape detection based on aspect ratio
        height, width = img_bgr.shape[:2]
        aspect_ratio = width / height if height > 0 else 1
        
        # Find closest match based on color and shape
        best_match = None
        best_score = float('inf')
        
        for piece_type, template in PIECE_TEMPLATES.items():
            # Color distance
            color_diff = np.linalg.norm(np.array(avg_color) - np.array(template["avg_color"]))
            
            # Shape score (simple aspect ratio matching)
            if template["shape"] == "tall" and aspect_ratio < 0.8:
                shape_score = 0
            elif template["shape"] == "square" and 0.8 <= aspect_ratio <= 1.2:
                shape_score = 0
            elif template["shape"] in ["t-shape", "z-shape", "l-shape"] and 0.8 <= aspect_ratio <= 1.5:
                shape_score = 0
            else:
                shape_score = 10  # Penalty for wrong shape
            
            total_score = color_diff + shape_score
            
            if total_score < best_score:
                best_score = total_score
                best_match = piece_type
        
        return best_match
        
    except Exception as e:
        log.error(f"Error detecting piece: {e}")
        return None

def get_current_piece() -> Optional[str]:
    """Get the current piece from the next queue (first slot)."""
    try:
        queue_images = capture_next_queue()
        if not queue_images:
            log.warning("No queue images captured")
            return None
        
        # Detect piece from the first queue slot
        current_piece = detect_piece_from_image(queue_images[0])
        
        if current_piece:
            log.debug(f"Detected current piece: {current_piece}")
        else:
            log.debug("Could not detect piece type, using default")
        
        return current_piece
        
    except Exception as e:
        log.error(f"Error getting current piece: {e}")
        return None

def get_next_pieces(count: int = 3) -> List[str]:
    """Get the next pieces from the queue."""
    pieces = []
    try:
        queue_images = capture_next_queue()
        
        for i in range(min(count, len(queue_images))):
            piece = detect_piece_from_image(queue_images[i])
            pieces.append(piece or "T")  # Default to T if detection fails
            
    except Exception as e:
        log.error(f"Error getting next pieces: {e}")
    
    return pieces

if __name__ == "__main__":
    # Test the piece detector
    piece = get_current_piece()
    print(f"Current piece: {piece}")
    
    next_pieces = get_next_pieces(3)
    print(f"Next pieces: {next_pieces}")
