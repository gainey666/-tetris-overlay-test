import cv2, numpy as np, os
from pathlib import Path

# Put a screenshot of the Tetris board (with pieces) in the same folder as this script
IMG = Path("board_sample.png")
if not IMG.is_file():
    raise FileNotFoundError(
        "Place a screenshot of the board named board_sample.png next to this script"
    )

# Manual ROI for a single cell (set once, then use for all templates)
# Change these numbers to match the size of one block in your screenshot
CELL_W, CELL_H = 30, 30  # example size
TOP_LEFT_X, TOP_LEFT_Y = 100, 200  # top-left corner of the board in the screenshot

templates_dir = Path(__file__).parent.parent / "src" / "templates"
templates_dir.mkdir(exist_ok=True)

# Define the 7 tetrominos (relative block coordinates)
tetrominos = {
    "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}


# 4 rotations for each piece
def rotate(shape):
    return [(-y, x) for x, y in shape]


for name, blocks in tetrominos.items():
    cur = blocks
    for rot in range(4):
        # create empty cell image (20x10 cells → 200x100 pixels for matching)
        img = np.zeros((100, 200), dtype=np.uint8)
        for x, y in cur:
            px = TOP_LEFT_X + (x * CELL_W)
            py = TOP_LEFT_Y + (y * CELL_H)
            cv2.rectangle(img, (px, py), (px + CELL_W, py + CELL_H), 255, -1)
        # downscale to board size (20x10) for matching
        tmpl = cv2.resize(img, (200, 100), interpolation=cv2.INTER_NEAREST)
        out_path = templates_dir / f"{name}_{rot}.png"
        cv2.imwrite(str(out_path), tmpl)
        cur = rotate(cur)
print("Templates generated under:", templates_dir)
