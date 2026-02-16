import json
from pathlib import Path

import tkinter as tk
from PIL import ImageTk
import mss

from capture import ScreenCapture
from dual_roi_manager import set_roi_pair

ROI_CONFIG_PATH = Path("config/roi_config.json")

ROI_SEQUENCE = [
    ("player_left_board", "Draw PLAYER LEFT board (main grid)."),
    ("player_right_board", "Draw PLAYER RIGHT board."),
    ("left_hold_piece", "Draw LEFT hold-piece box."),
    ("right_hold_piece", "Draw RIGHT hold-piece box."),
    ("left_next_preview", "Draw LEFT next-piece preview."),
    ("right_next_preview", "Draw RIGHT next-piece preview."),
    ("left_garbage_indicator", "Draw LEFT garbage indicator."),
    ("right_garbage_indicator", "Draw RIGHT garbage indicator."),
    ("left_zone_meter", "Draw LEFT zone meter."),
    ("right_zone_meter", "Draw RIGHT zone meter."),
    ("left_score", "Draw LEFT score region."),
    ("right_score", "Draw RIGHT score region."),
    ("left_player_name", "Draw LEFT player-name banner."),
    ("right_player_name", "Draw RIGHT player-name banner."),
    ("wins", "Draw WINS banner (label plus both player dots)."),
    ("timer", "Draw GLOBAL match timer display."),
]

# Define expected next queue slots for both players
NEXT_QUEUE_SLOTS = {
    "left": [f"left_next_queue_slot_{i+1}" for i in range(4)],
    "right": [f"right_next_queue_slot_{i+1}" for i in range(4)],
}


def _load_existing_config():
    if not ROI_CONFIG_PATH.exists():
        return {}, {}, {}
    try:
        with ROI_CONFIG_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}, {}, {}
    rects = {}
    left_queue_rects = {}
    right_queue_rects = {}
    for entry in data.get("rois", []):
        name = entry.get("name")
        rect = entry.get("rect")
        if not name or rect is None:
            continue
        
        # Handle legacy next_queue format
        if name == "next_queue" and isinstance(rect, list):
            # Legacy format: split into left slots (assume all were left)
            for i, slot_rect in enumerate(rect[:4]):
                slot_name = f"left_next_queue_slot_{i+1}"
                left_queue_rects[slot_name] = slot_rect
            continue
        
        # Handle individual queue slots
        if name.startswith("left_next_queue_slot_"):
            left_queue_rects[name] = rect
        elif name.startswith("right_next_queue_slot_"):
            right_queue_rects[name] = rect
        else:
            rects[name] = rect
    
    return rects, left_queue_rects, right_queue_rects


def _normalize_rect(rect):
    return [int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])]


def _prompt_queue_target() -> int:
    default = 4
    try:
        resp = input(
            "How many next-queue slots should be captured (1-4, default 4)? "
        ).strip()
    except Exception:
        return default
    if not resp:
        return default
    try:
        value = int(resp)
    except ValueError:
        return default
    return max(1, min(4, value))


def _save_roi_config(entries, left_queue_rects, right_queue_rects):
    # Convert queue dicts to list format for saving
    queue_entries = []
    for name, rect in left_queue_rects.items():
        queue_entries.append({"name": name, "rect": rect})
    for name, rect in right_queue_rects.items():
        queue_entries.append({"name": name, "rect": rect})
    
    data = {
        "rois": entries + queue_entries,
        "hwnd": None,
    }
    with ROI_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    total_rois = len(entries) + len(left_queue_rects) + len(right_queue_rects)
    print(f"Saved {total_rois} ROIs to {ROI_CONFIG_PATH}")


def start_calibrator():
    root = tk.Tk()
    root.title("ROI Calibration – follow console prompts")

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width, height = monitor["width"], monitor["height"]

    capture = ScreenCapture((0, 0, width, height))
    screenshot = capture.grab()

    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    photo = ImageTk.PhotoImage(screenshot)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    root._background_photo = photo  # keep reference to avoid GC

    entries = []
    board_rects = []
    left_queue_rects = {}
    right_queue_rects = {}
    rect_id = None
    start_pos = None
    current_index = 0
    queue_mode = False
    queue_target = 4
    queue_side = "left"  # Track which side we're capturing
    existing_rois, existing_left_queue, existing_right_queue = _load_existing_config()

    def print_order():
        print("ROI calibration order:")
        for idx, (_, msg) in enumerate(ROI_SEQUENCE, start=1):
            print(f"  {idx}. {msg}")
        print("Then draw up to four next-queue slots.")

    print_order()
    if existing_rois or existing_left_queue or existing_right_queue:
        print(
            "Loaded saved ROI data. During confirmation you can press 'K' to keep the stored rectangle."
        )

    # Show existing ROIs as visual overlays on startup
    def show_existing_rois():
        """Display all existing ROIs as colored overlays"""
        # Show main ROIs in green
        for name, rect in existing_rois.items():
            mark_rect(rect, f"{name} (saved)", "green")
        
        # Show left queue slots in green
        for name, rect in existing_left_queue.items():
            mark_rect(rect, f"{name} (saved)", "green")
        
        # Show right queue slots in green
        for name, rect in existing_right_queue.items():
            mark_rect(rect, f"{name} (saved)", "green")
        
        # Show missing queue slots as red placeholders
        # Left queue
        for slot_name in NEXT_QUEUE_SLOTS["left"]:
            if slot_name not in existing_left_queue:
                # Estimate position based on left_next_preview
                if "left_next_preview" in existing_rois:
                    base_rect = existing_rois["left_next_preview"]
                    # Stack below the preview box
                    slot_index = int(slot_name.split("_")[-1]) - 1
                    placeholder = [
                        base_rect[0],  # same x
                        base_rect[1] + base_rect[3] + 10 + (slot_index * 35),  # below preview
                        base_rect[2],  # same width
                        30  # height
                    ]
                    mark_rect(placeholder, f"{slot_name} (missing)", "red")
        
        # Right queue
        for slot_name in NEXT_QUEUE_SLOTS["right"]:
            if slot_name not in existing_right_queue:
                # Estimate position based on right_next_preview
                if "right_next_preview" in existing_rois:
                    base_rect = existing_rois["right_next_preview"]
                    # Stack below the preview box
                    slot_index = int(slot_name.split("_")[-1]) - 1
                    placeholder = [
                        base_rect[0],  # same x
                        base_rect[1] + base_rect[3] + 10 + (slot_index * 35),  # below preview
                        base_rect[2],  # same width
                        30  # height
                    ]
                    mark_rect(placeholder, f"{slot_name} (missing)", "red")
    
    show_existing_rois()

    confirmed_items: list[int] = []

    def mark_rect(rect, label, color):
        left, top, width, height = rect
        box = canvas.create_rectangle(
            left,
            top,
            left + width,
            top + height,
            outline=color,
            width=2,
        )
        text = canvas.create_text(
            left + 4,
            top + 12,
            anchor=tk.NW,
            text=label,
            fill=color,
            font=("Helvetica", 11, "bold"),
        )
        confirmed_items.extend([box, text])
        return box, text

    def clear_confirmed():
        nonlocal confirmed_items
        for cid in confirmed_items:
            canvas.delete(cid)
        confirmed_items = []

    def prompt_next():
        if queue_mode:
            current_queue = left_queue_rects if queue_side == "left" else right_queue_rects
            existing_queue = existing_left_queue if queue_side == "left" else existing_right_queue
            remaining = queue_target - len(current_queue)
            hint = ""
            if len(current_queue) < len(existing_queue):
                hint = " (press K to keep saved slot)"
            print(
                f"Draw {queue_side} next-queue rectangle ({len(current_queue)+1}/{queue_target}). {remaining} left.{hint}"
            )
        elif current_index < len(ROI_SEQUENCE):
            name, message = ROI_SEQUENCE[current_index]
            hint = ""
            if name in existing_rois:
                hint = " (press K to reuse saved rect)"
            print(f"[{current_index+1}/{len(ROI_SEQUENCE)}] {message}{hint}")

    prompt_next()

    def begin_queue_mode():
        nonlocal queue_mode, queue_target, queue_side
        queue_mode = True
        queue_target = _prompt_queue_target()
        
        # Capture left queue first, then right
        queue_side = "left"
        print(
            f"Capturing {queue_target} LEFT next-queue slot(s). Draw them in order from top to bottom."
        )
        prompt_next()

    def reset_calibration():
        nonlocal entries, board_rects, left_queue_rects, right_queue_rects, current_index, queue_mode, queue_target, queue_side
        print("Restarting calibration from step 1...")
        entries = []
        board_rects = []
        left_queue_rects = {}
        right_queue_rects = {}
        current_index = 0
        queue_mode = False
        queue_target = 4
        queue_side = "left"
        clear_confirmed()
        print_order()
        prompt_next()

    def finalize():
        if len(board_rects) == 2:
            set_roi_pair(board_rects)
        _save_roi_config(entries, left_queue_rects, right_queue_rects)
        root.destroy()

    def confirm_capture(label, rect, allow_keep=False):
        extra = "/K" if allow_keep else ""
        while True:
            resp = (
                input(f"Captured {label}: {rect}. Keep this? [Y/N/E{extra}] ")
                .strip()
                .lower()
            )
            if resp in ("y", "yes"):
                return "accept"
            if resp in ("n", "no"):
                return "redo"
            if resp in ("e", "exit"):
                return "restart"
            if allow_keep and resp in ("k", "keep"):
                return "keep"
            print("Please respond with Y (yes), N (no), or E (exit & restart).")

    def on_mouse_down(event):
        nonlocal start_pos, rect_id
        start_pos = (event.x, event.y)
        if rect_id:
            canvas.delete(rect_id)
        rect_id = None

    def on_mouse_motion(event):
        nonlocal rect_id, start_pos
        if start_pos:
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(
                start_pos[0], start_pos[1], event.x, event.y, outline="red", width=2
            )

    def on_mouse_up(event):
        nonlocal start_pos, rect_id, current_index, queue_side
        if not start_pos:
            return

        left = min(start_pos[0], event.x)
        top = min(start_pos[1], event.y)
        width_rect = abs(event.x - start_pos[0])
        height_rect = abs(event.y - start_pos[1])
        rect = [left, top, width_rect, height_rect]

        if queue_mode:
            current_queue = left_queue_rects if queue_side == "left" else right_queue_rects
            existing_queue = existing_left_queue if queue_side == "left" else existing_right_queue
            slot_index = len(current_queue)
            label = f"{queue_side}_next_queue_slot_{slot_index+1}"
            allow_keep = slot_index < len(existing_queue)
        else:
            label = ROI_SEQUENCE[current_index][0]
            allow_keep = label in existing_rois

        decision = confirm_capture(label, rect, allow_keep=allow_keep)

        if decision == "restart":
            if rect_id:
                canvas.delete(rect_id)
                rect_id = None
            start_pos = None
            reset_calibration()
            return
        if decision == "redo":
            if rect_id:
                canvas.delete(rect_id)
                rect_id = None
            start_pos = None
            prompt_next()
            return

        if rect_id:
            canvas.delete(rect_id)
            rect_id = None

        if decision == "keep":
            if queue_mode:
                current_queue = left_queue_rects if queue_side == "left" else right_queue_rects
                existing_queue = existing_left_queue if queue_side == "left" else existing_right_queue
                if slot_index >= len(existing_queue):
                    print("No saved queue rect available; please redraw.")
                    prompt_next()
                    start_pos = None
                    return
                rect = _normalize_rect(list(existing_queue.values())[slot_index])
                current_queue[label] = rect
            else:
                saved = existing_rois.get(label)
                if not saved:
                    print("No saved ROI for this entry; please redraw.")
                    prompt_next()
                    start_pos = None
                    return
                rect = _normalize_rect(saved)
                entries.append({"name": label, "rect": rect})
                if label in ("player_left_board", "player_right_board"):
                    board_rects.append(rect)
                current_index += 1
            mark_rect(rect, f"{label} (saved)", "cyan")
        else:
            # accept case
            if queue_mode:
                current_queue = left_queue_rects if queue_side == "left" else right_queue_rects
                current_queue[label] = rect
            else:
                name, _ = ROI_SEQUENCE[current_index]
                entries.append({"name": name, "rect": rect})
                if name in ("player_left_board", "player_right_board"):
                    board_rects.append(rect)
                current_index += 1
            mark_rect(rect, label, "lime")

        if queue_mode:
            current_queue = left_queue_rects if queue_side == "left" else right_queue_rects
            if len(current_queue) >= queue_target:
                if queue_side == "left":
                    # Switch to right queue
                    queue_side = "right"
                    print(f"\nCapturing {queue_target} RIGHT next-queue slot(s). Draw them in order from top to bottom.")
                    prompt_next()
                else:
                    # Both sides done
                    finalize()
            else:
                prompt_next()
        else:
            if current_index >= len(ROI_SEQUENCE):
                begin_queue_mode()
            else:
                prompt_next()

        start_pos = None

    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_motion)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()


if __name__ == "__main__":
    start_calibrator()
