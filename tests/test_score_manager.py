"""Unit tests for ScoreManager."""

import unittest
from unittest.mock import MagicMock

from src.interactors.score_manager import ScoreManager


class TestScoreManager(unittest.TestCase):
    """Tests for the ScoreManager class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.score1 = MagicMock()
        self.score2 = MagicMock()
        self.manager = ScoreManager(self.score1, self.score2)

    def test_initial_scores_are_zero(self) -> None:
        """Test that initial scores are zero."""
        self.assertEqual(self.manager.score, [0, 0])

    def test_score_point_player1(self) -> None:
        """Test scoring a point for player 1."""
        self.manager.score_point(1)
        self.assertEqual(self.manager.score, [1, 0])
        self.score1.SetInput.assert_called_with("1")

    def test_score_point_player2(self) -> None:
        """Test scoring a point for player 2."""
        self.manager.score_point(2)
        self.assertEqual(self.manager.score, [0, 1])
        self.score2.SetInput.assert_called_with("1")

    def test_multiple_score_points(self) -> None:
        """Test scoring multiple points."""
        self.manager.score_point(1)
        self.manager.score_point(1)
        self.manager.score_point(2)
        self.assertEqual(self.manager.score, [2, 1])

    def test_reset_scores(self) -> None:
        """Test resetting scores to zero."""
        self.manager.score_point(1)
        self.manager.score_point(2)
        self.manager.reset()
        self.assertEqual(self.manager.score, [0, 0])


if __name__ == "__main__":
    unittest.main()
