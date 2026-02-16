import cv2, numpy as np
from pathlib import Path


def create_dummy_board():
    # Create a simple 20x10 Tetris board with a few pieces
    board = np.zeros((200, 100, 3), dtype=np.uint8)  # 10x height for visibility

    # Add some random pieces (blocks)
    # I piece horizontal at top
    board[10:20, 20:60] = [255, 255, 255]
    # O piece
    board[30:50, 10:30] = [255, 255, 255]
    # T piece
    board[50:70, 40:80] = [255, 255, 255]
    board[70:90, 50:70] = [255, 255, 255]

    # Add grid lines for clarity
    for i in range(11):
        board[:, i * 10 : i * 10 + 1] = [128, 128, 128]
    for i in range(21):
        board[i * 10 : i * 10 + 1, :] = [128, 128, 128]

    # Save
    out_path = Path(__file__).parent / "board_sample.png"
    cv2.imwrite(str(out_path), board)
    print(f"Created dummy board image: {out_path}")


if __name__ == "__main__":
    create_dummy_board()
