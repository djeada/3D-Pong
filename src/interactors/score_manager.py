"""Score manager module for tracking and displaying player scores."""

import logging
from typing import List

import vtk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ScoreManager:
    """Manager for tracking and displaying player scores."""

    def __init__(self, score1: vtk.vtkTextActor, score2: vtk.vtkTextActor) -> None:
        """
        Initialize the score manager.

        Args:
            score1: The text actor for player 1's score.
            score2: The text actor for player 2's score.
        """
        self.score1 = score1
        self.score2 = score2
        self.score: List[int] = [0, 0]

    def update_score_display(self) -> None:
        """Update the score display text actors."""
        self.score1.SetInput(str(self.score[0]))
        self.score2.SetInput(str(self.score[1]))
        logging.debug(
            f"Scores updated. Player 1: {self.score[0]}, Player 2: {self.score[1]}"
        )

    def score_point(self, player: int) -> None:
        """
        Award a point to the specified player.

        Args:
            player: The player number (1 or 2) to award the point to.
        """
        if player == 1:
            self.score[0] += 1
        else:
            self.score[1] += 1
        self.update_score_display()

    def reset(self) -> None:
        """Reset both players' scores to zero."""
        self.score = [0, 0]
        self.update_score_display()
        logging.info("Scores reset to 0-0.")
