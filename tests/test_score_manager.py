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

    def test_default_win_score(self) -> None:
        """Test that default win score is 11."""
        self.assertEqual(self.manager.win_score, 11)

    def test_custom_win_score(self) -> None:
        """Test setting custom win score."""
        manager = ScoreManager(self.score1, self.score2, win_score=5)
        self.assertEqual(manager.win_score, 5)

    def test_win_condition_player1(self) -> None:
        """Test win condition when player 1 reaches win score."""
        manager = ScoreManager(self.score1, self.score2, win_score=3)
        game_over_called = []
        manager.on_game_over = lambda winner: game_over_called.append(winner)

        manager.score_point(1)
        manager.score_point(1)
        self.assertFalse(manager.game_over)
        manager.score_point(1)
        self.assertTrue(manager.game_over)
        self.assertEqual(game_over_called, [1])

    def test_win_condition_player2(self) -> None:
        """Test win condition when player 2 reaches win score."""
        manager = ScoreManager(self.score1, self.score2, win_score=3)
        game_over_called = []
        manager.on_game_over = lambda winner: game_over_called.append(winner)

        for _ in range(3):
            manager.score_point(2)
        self.assertTrue(manager.game_over)
        self.assertEqual(game_over_called, [2])

    def test_no_scoring_after_game_over(self) -> None:
        """Test that scoring is blocked after game over."""
        manager = ScoreManager(self.score1, self.score2, win_score=3)
        for _ in range(3):
            manager.score_point(1)
        self.assertEqual(manager.score, [3, 0])

        # Try to score more
        manager.score_point(1)
        manager.score_point(2)
        self.assertEqual(manager.score, [3, 0])

    def test_get_winner(self) -> None:
        """Test getting the winner."""
        manager = ScoreManager(self.score1, self.score2, win_score=3)
        self.assertIsNone(manager.get_winner())

        for _ in range(3):
            manager.score_point(1)
        self.assertEqual(manager.get_winner(), 1)

    def test_reset_clears_game_over(self) -> None:
        """Test that reset clears game over state."""
        manager = ScoreManager(self.score1, self.score2, win_score=3)
        for _ in range(3):
            manager.score_point(1)
        self.assertTrue(manager.game_over)

        manager.reset()
        self.assertFalse(manager.game_over)
        self.assertEqual(manager.score, [0, 0])


if __name__ == "__main__":
    unittest.main()
