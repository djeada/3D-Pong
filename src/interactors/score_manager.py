"""Score manager module for tracking and displaying player scores."""

import logging
from typing import Callable, List

import vtk

logger = logging.getLogger(__name__)


class ScoreManager:
    """
    Manager for tracking and displaying player scores.

    Includes win condition detection and game over callbacks.
    """

    DEFAULT_WIN_SCORE = 11

    def __init__(
        self,
        score1: vtk.vtkTextActor,
        score2: vtk.vtkTextActor,
        win_score: int = DEFAULT_WIN_SCORE,
    ) -> None:
        """
        Initialize the score manager.

        Args:
            score1: The text actor for player 1's score.
            score2: The text actor for player 2's score.
            win_score: Score needed to win the game.
        """
        self.score1 = score1
        self.score2 = score2
        self.score: List[int] = [0, 0]
        self.win_score = win_score
        self.on_game_over: Callable[[int], None] | None = None
        self.game_over = False

    def update_score_display(self) -> None:
        """Update the score display text actors."""
        self.score1.SetInput(str(self.score[0]))
        self.score2.SetInput(str(self.score[1]))
        logger.debug(
            f"Scores updated. Player 1: {self.score[0]}, Player 2: {self.score[1]}"
        )

    def score_point(self, player: int) -> None:
        """
        Award a point to the specified player.

        Args:
            player: The player number (1 or 2) to award the point to.
        """
        if self.game_over:
            return

        if player == 1:
            self.score[0] += 1
        else:
            self.score[1] += 1
        self.update_score_display()
        self._check_win_condition()

    def _check_win_condition(self) -> None:
        """Check if a player has won and trigger game over."""
        winner = None
        if self.score[0] >= self.win_score:
            winner = 1
        elif self.score[1] >= self.win_score:
            winner = 2

        if winner:
            self.game_over = True
            logger.info(f"Player {winner} wins!")
            if self.on_game_over:
                self.on_game_over(winner)

    def reset(self) -> None:
        """Reset both players' scores to zero."""
        self.score = [0, 0]
        self.game_over = False
        self.update_score_display()
        logger.info("Scores reset to 0-0.")

    def get_winner(self) -> int | None:
        """
        Get the winner if game is over.

        Returns:
            Player number (1 or 2) if there's a winner, None otherwise.
        """
        if self.score[0] >= self.win_score:
            return 1
        elif self.score[1] >= self.win_score:
            return 2
        return None

    def set_win_score(self, win_score: int) -> None:
        """
        Set the score needed to win.

        Args:
            win_score: New win score threshold.
        """
        self.win_score = max(1, win_score)
        logger.info(f"Win score set to {self.win_score}")
