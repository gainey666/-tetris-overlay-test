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


def _load_existing_config():
    if not ROI_CONFIG_PATH.exists():
        return {}, []
    try:
        with ROI_CONFIG_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}, []
    rects = {}
    queue_rects = []
    for entry in data.get("rois", []):
        name = entry.get("name")
        rect = entry.get("rect")
        if not name or rect is None:
            continue
        if name == "next_queue" and isinstance(rect, list) and rect and isinstance(rect[0], list):
            queue_rects = rect
            continue
        rects[name] = rect
    return rects, queue_rects


def _normalize_rect(rect):
    return [int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])]


def _prompt_queue_target() -> int:
    default = 4
    try:
        resp = input("How many next-queue slots should be captured (1-4, default 4)? ").strip()
    except Exception:
        return default
    if not resp:
        return default
    try:
        value = int(resp)
    except ValueError:
        return default
    return max(1, min(4, value))


def _save_roi_config(entries, queue_rects):
    data = {
        "rois": entries + [{"name": "next_queue", "rect": queue_rects}],
        "hwnd": None,
    }
    with ROI_CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Saved {len(entries)} ROIs (+next_queue) to {ROI_CONFIG_PATH}")


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
    queue_rects = []
    rect_id = None
    start_pos = None
    current_index = 0
    queue_mode = False
    queue_target = 4
    existing_rois, existing_queue = _load_existing_config()

    def print_order():
        print("ROI calibration order:")
        for idx, (_, msg) in enumerate(ROI_SEQUENCE, start=1):
            print(f"  {idx}. {msg}")
        print("Then draw up to four next-queue slots.")

    print_order()
    if existing_rois or existing_queue:
        print("Loaded saved ROI data. During confirmation you can press 'K' to keep the stored rectangle.")

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
            remaining = queue_target - len(queue_rects)
            hint = ""
            if len(queue_rects) < len(existing_queue):
                hint = " (press K to keep saved slot)"
            print(
                f"Draw next-queue rectangle ({len(queue_rects)+1}/{queue_target}). {remaining} left.{hint}"
            )
        elif current_index < len(ROI_SEQUENCE):
            name, message = ROI_SEQUENCE[current_index]
            hint = ""
            if name in existing_rois:
                hint = " (press K to reuse saved rect)"
            print(f"[{current_index+1}/{len(ROI_SEQUENCE)}] {message}{hint}")

    prompt_next()

    def begin_queue_mode():
        nonlocal queue_mode, queue_target
        queue_mode = True
        queue_target = _prompt_queue_target()
        print(f"Capturing {queue_target} next-queue slot(s). Draw them in order from top to bottom.")
        prompt_next()

    def reset_calibration():
        nonlocal entries, board_rects, queue_rects, current_index, queue_mode, queue_target
        print("Restarting calibration from step 1...")
        entries = []
        board_rects = []
        queue_rects = []
        current_index = 0
        queue_mode = False
        queue_target = 4
        clear_confirmed()
        print_order()
        prompt_next()

    def finalize():
        if len(board_rects) == 2:
            set_roi_pair(board_rects)
        _save_roi_config(entries, queue_rects)
        root.destroy()

    def confirm_capture(label, rect, allow_keep=False):
        extra = "/K" if allow_keep else ""
        while True:
            resp = input(
                f"Captured {label}: {rect}. Keep this? [Y/N/E{extra}] "
            ).strip().lower()
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
        nonlocal start_pos, rect_id, current_index
        if not start_pos:
            return

        left = min(start_pos[0], event.x)
        top = min(start_pos[1], event.y)
        width_rect = abs(event.x - start_pos[0])
        height_rect = abs(event.y - start_pos[1])
        rect = [left, top, width_rect, height_rect]

        slot_index = len(queue_rects)
        label = (
            f"next_queue slot {slot_index+1}/{queue_target}"
            if queue_mode
            else ROI_SEQUENCE[current_index][0]
        )
        allow_keep = (
            slot_index < len(existing_queue)
            if queue_mode
            else label in existing_rois
        )

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
                if slot_index >= len(existing_queue):
                    print("No saved queue rect available; please redraw.")
                    prompt_next()
                    start_pos = None
                    return
                rect = _normalize_rect(existing_queue[slot_index])
                queue_rects.append(rect)
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
                queue_rects.append(rect)
            else:
                name, _ = ROI_SEQUENCE[current_index]
                entries.append({"name": name, "rect": rect})
                if name in ("player_left_board", "player_right_board"):
                    board_rects.append(rect)
                current_index += 1
            mark_rect(rect, label, "lime")

        if queue_mode:
            if len(queue_rects) >= queue_target:
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
