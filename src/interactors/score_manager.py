import logging
from typing import Any, Dict, List

import vtk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ScoreManager:
    def __init__(self, score1: vtk.vtkTextActor, score2: vtk.vtkTextActor) -> None:
        self.score1 = score1
        self.score2 = score2
        self.score: List[int] = [0, 0]

    def update_score_display(self) -> None:
        self.score1.SetInput(str(self.score[0]))
        self.score2.SetInput(str(self.score[1]))
        logging.debug(
            f"Scores updated. Player 1: {self.score[0]}, Player 2: {self.score[1]}"
        )

    def score_point(self, player: int) -> None:
        if player == 1:
            self.score[0] += 1
        else:
            self.score[1] += 1
        self.update_score_display()
