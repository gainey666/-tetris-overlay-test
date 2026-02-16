# Hotkeys Reference

## Global Hotkeys

| Hotkey | Action | Description |
|--------|--------|-------------|
| **Esc** | Exit | Gracefully shutdown the overlay |
| **F9** | Toggle Overlay | Show/hide the ghost piece overlay |
| **F1** | Legacy Calibration | Opens the old pygame-based calibration (deprecated) |
| **F2** | Toggle Debug Logging | Switch between INFO and DEBUG log levels |
| **Ctrl+Alt+C** | ROI Calibration | Opens the new visual ROI calibrator |

## Calibration Workflow (Ctrl+Alt+C)

1. **Main ROIs (16 items)** - Draw rectangles for:
   - Player boards (left/right)
   - Hold pieces (left/right)
   - Next piece previews (left/right)
   - Garbage indicators (left/right)
   - Zone meters (left/right)
   - Score regions (left/right)
   - Player names (left/right)
   - Wins banner
   - Match timer

2. **Next Queue Slots** - Draw 4 slots for each player:
   - LEFT next queue (4 slots stacked below preview)
   - RIGHT next queue (4 slots stacked below preview)

3. **Key Controls during calibration:**
   - **Y** - Accept and keep the drawn rectangle
   - **N** - Redraw the rectangle
   - **E** - Exit and restart calibration
   - **K** - Keep the saved rectangle (if available)

## Visual Indicators

- **Green boxes** - Previously saved ROIs (will be kept with 'K')
- **Red boxes** - Missing ROIs (need to be drawn)
- **White outline** - Currently drawing rectangle

## Tips

- Press 'K' to quickly reuse existing ROIs without redrawing
- The calibrator shows visual feedback - you can see exactly what's missing
- After calibration, the overlay will show ghost pieces at predicted positions
- Toggle the overlay with F9 if it's in the way
