# ---- prediction_agent_dellacherie.py ---------------------------------
import numpy as np
from .base_agent import BaseAgent

# ----------------------------------------------------------------------
# Helper: generate all legal placements for a given piece & orientation
# ----------------------------------------------------------------------
PIECE_SHAPES = {
    # Each piece: list of rotations; each rotation is a list of (x,y) cells
    "I": [
        [(0,0),(1,0),(2,0),(3,0)],
        [(0,0),(0,1),(0,2),(0,3)],
    ],
    "O": [
        [(0,0),(1,0),(0,1),(1,1)],
    ],
    "T": [
        [(0,0),(1,0),(2,0),(1,1)],
        [(1,0),(0,1),(1,1),(1,2)],
        [(1,0),(0,1),(1,1),(2,1)],
        [(0,0),(0,1),(1,1),(0,2)],
    ],
    "S": [
        [(1,0),(2,0),(0,1),(1,1)],
        [(0,0),(0,1),(1,1),(1,2)],
    ],
    "Z": [
        [(0,0),(1,0),(1,1),(2,1)],
        [(1,0),(0,1),(1,1),(0,2)],
    ],
    "J": [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,0),(1,0),(2,0),(2,1)],
        [(1,0),(1,1),(0,2),(1,2)],
    ],
    "L": [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,0),(1,0),(2,0),(0,1)],
        [(0,0),(1,0),(1,1),(1,2)],
    ],
}

# ----------------------------------------------------------------------
# Scoring terms (weights tuned for Tetris Effect style play)
# ----------------------------------------------------------------------
W_HEIGHT       = -0.510066   # aggregate column height (lower is better)
W_LINES        =  0.760666   # lines cleared in this placement
W_HOLES        = -0.35663    # empty cells with a block above
W_BUMPINESS    = -0.184483   # sum of height differences between columns
W_WELL_DEPTH   = -0.5        # deeper wells are penalised (helps avoid "tower")
W_TSPIN        =  1.0        # bonus for a successful T‑Spin
W_B2B          =  0.8        # back‑to‑back bonus (T‑Spin or Tetris)
W_COMBO        =  0.3        # incremental combo reward

class PredictionAgent(BaseAgent):
    """
    Dellacherie‑style heuristic AI.
    Input params (dict):
        board          – 20×10 uint8 binary matrix (0 = empty, 255 = block)
        piece          – one‑character string: I,O,T,S,Z,J,L
        orientation    – 0‑3 (index into PIECE_SHAPES[piece])
        hold           – optional held piece (unused here, kept for future extensions)
    Returns dict:
        target_col, target_rot, is_tspin, is_b2b, combo (int)
    """
    def __init__(self):
        self.prev_clear = 0          # lines cleared in previous move (for B2B)
        self.prev_was_tspin = False # for B2B chain detection
        self.combo = 0               # ongoing combo counter

    def start(self):
        """No-op for compatibility with existing orchestrator."""
        pass

    def stop(self):
        """No-op for compatibility with existing orchestrator."""
        pass

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def handle(self, params):
        board   = params["board"]
        piece   = params["piece"]
        orient  = params["orientation"]
        hold    = params.get("hold")   # not used now

        best = None
        best_score = -float("inf")
        best_is_tspin = False
        best_is_b2b = False

        # --------------------------------------------------------------
        # iterate every legal column for this rotation
        # --------------------------------------------------------------
        shape = PIECE_SHAPES[piece][orient]
        max_x = max(x for x, _ in shape)
        for col in range(10 - max_x):
            # simulate dropping the piece
            landed_board, lines_cleared, is_tspin = self._drop_piece(board, shape, col, piece)

            # ----------------------------------------------------------------
            # evaluate the resulting board
            # ----------------------------------------------------------------
            agg_h, holes, bumpiness, well = self._board_metrics(landed_board)
            score = (W_HEIGHT * agg_h +
                     W_LINES  * lines_cleared +
                     W_HOLES * holes +
                     W_BUMPINESS * bumpiness +
                     W_WELL_DEPTH * well)

            # ---- T‑Spin / B2B / Combo bonuses ----
            if is_tspin:
                score += W_TSPIN
                # B2B is granted when this T‑Spin follows another T‑Spin or a Tetris
                if self.prev_was_tspin or self.prev_clear == 4:
                    score += W_B2B
                    best_is_b2b = True
                self.prev_was_tspin = True
                self.prev_clear = lines_cleared
            else:
                # regular line clear – check B2B for Tetris (4 lines)
                if lines_cleared == 4:
                    if self.prev_clear == 4:
                        score += W_B2B
                        best_is_b2b = True
                    self.prev_was_tspin = False
                else:
                    self.prev_was_tspin = False
                self.prev_clear = lines_cleared

            # combo: every successive line‑clear adds a small bump
            if lines_cleared > 0:
                self.combo += 1
                score += W_COMBO * self.combo
            else:
                self.combo = 0

            if score > best_score:
                best_score = score
                best = (col, orient)
                best_is_tspin = is_tspin
                best_is_b2b = best_is_b2b

        # --------------------------------------------------------------------
        # Return the best move
        # --------------------------------------------------------------------
        col, rot = best
        return {
            "target_col": col,
            "target_rot": rot,
            "is_tspin": bool(best_is_tspin),
            "is_b2b":   bool(best_is_b2b),
            "combo":    self.combo,
        }

    # ------------------------------------------------------------------
    # Drop a piece onto the board, return new board + cleared lines + tspin flag
    # ------------------------------------------------------------------
    def _drop_piece(self, board, shape, col, piece):
        # Copy board to avoid mutating the original
        b = board.copy()
        # piece starts high enough (y = -max_y)
        max_y = max(y for _, y in shape)
        y = -max_y
        # keep moving down until collision
        while True:
            collision = False
            for dx, dy in shape:
                bx = col + dx
                by = y + dy + 1
                if by >= 20:                     # bottom of the well
                    collision = True
                    break
                if b[by, bx] == 255:            # block already present
                    collision = True
                    break
            if collision:
                break
            y += 1

        # lock piece at final (col, y)
        for dx, dy in shape:
            bx = col + dx
            by = y + dy
            b[by, bx] = 255

        # ---- T‑Spin detection (only for T piece) -----------------------
        is_tspin = False
        if piece == "T":   # any T rotation qualifies
            # Count occupied corners around the T's central block
            cx = col + 1
            cy = y + 1
            corners = 0
            for ox, oy in [( -1,-1),( 1,-1),(-1,1),(1,1)]:
                nx, ny = cx + ox, cy + oy
                if 0 <= nx < 10 and 0 <= ny < 20 and b[ny, nx] == 255:
                    corners += 1
            if corners >= 3:            # 3‑corner T‑Spin (standard)
                is_tspin = True

        # ---- line clear -------------------------------------------------
        cleared = 0
        new_rows = []
        for row in b:
            if np.all(row == 255):
                cleared += 1
            else:
                new_rows.append(row)
        # fill missing rows at top with empty rows
        while len(new_rows) < 20:
            new_rows.insert(0, np.zeros(10, dtype=np.uint8))
        new_board = np.stack(new_rows)

        return new_board, cleared, is_tspin

    # ------------------------------------------------------------------
    # Compute classic board metrics (height, holes, bumpiness, well depth)
    # ------------------------------------------------------------------
    def _board_metrics(self, board):
        heights = []
        holes = 0
        for col in range(10):
            column = board[:, col]
            # height = first occupied cell from top
            occupied = np.where(column == 255)[0]
            if len(occupied) == 0:
                h = 0
            else:
                h = 20 - occupied[0]
                # count holes below the top occupied cell
                holes += np.sum(column[occupied[0]:] == 0)
            heights.append(h)

        agg_height = sum(heights)
        # bumpiness = sum |h_i - h_{i+1}|
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(9))

        # well depth – deepest column surrounded by taller neighbours
        well = 0
        for i, h in enumerate(heights):
            left  = heights[i-1] if i > 0 else 20
            right = heights[i+1] if i < 9 else 20
            if h < left and h < right:
                well = max(well, min(left, right) - h)

        return agg_height, holes, bumpiness, well
# ----------------------------------------------------------------------
