import numpy as np, json, random, time
from src.agents.board_extractor_agent import BoardExtractorAgent
from src.agents.piece_detector_agent import PieceDetectorAgent
from src.agents.prediction_agent_mock_perfect import PredictionAgent

def random_board():
    rows = random.randint(0, 20)
    board = np.zeros((20,10), dtype=np.uint8)
    for r in range(rows):
        board[r] = np.random.choice([0,255], size=10, p=[0.3,0.7])
    return board

def perfect_ai(board, piece):
    # reuse the same PredictionAgent used by the pipeline
    from src.agents.prediction_agent_mock_perfect import PredictionAgent
    agent = PredictionAgent()
    out = agent.handle({"board": board, "piece": piece, "orientation":0})
    return {"target_col": out["target_col"], "target_rot": out["target_rot"]}

def main():
    extractor = BoardExtractorAgent()
    detector  = PieceDetectorAgent()
    predictor = PredictionAgent()
    total = 10000
    correct = 0
    start = time.perf_counter()
    for i in range(total):
        board = random_board()
        piece = random.choice(["I","O","T","S","Z","J","L"])
        params = {"board": board, "piece": piece, "orientation":0}
        pred = predictor.handle(params)
        perfect = perfect_ai(board, piece)
        if pred["target_col"] == perfect["target_col"] and pred["target_rot"] == perfect["target_rot"]:
            correct += 1
    elapsed = time.perf_counter() - start
    print(f"Accuracy: {correct/total*100:.2f}% ({correct}/{total}) in {elapsed:.1f}s")
if __name__=="__main__":
    main()
