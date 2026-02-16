from .base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    def handle(self, param):
        # naive: place at leftmost column
        return {"target_col": 0, "target_rot": param["orientation"]}
