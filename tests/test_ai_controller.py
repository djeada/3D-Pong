"""Unit tests for AIController."""

import unittest
from unittest.mock import MagicMock

from src.interactors.ai_controller import AIController


class TestAIController(unittest.TestCase):
    """Tests for the AIController class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.paddle = MagicMock()
        self.ball = MagicMock()
        self.paddle.GetPosition.return_value = (0.9, 0, 0)
        self.ball.GetPosition.return_value = (0, 0, 0)
        self.paddle_config = {"y_length": 0.4}

    def test_init_default_difficulty(self) -> None:
        """Test initialization with default difficulty."""
        controller = AIController(self.paddle, self.ball)
        self.assertEqual(controller.difficulty, AIController.DIFFICULTY_MEDIUM)

    def test_init_easy_difficulty(self) -> None:
        """Test initialization with easy difficulty."""
        controller = AIController(
            self.paddle, self.ball, AIController.DIFFICULTY_EASY
        )
        self.assertEqual(controller.difficulty, AIController.DIFFICULTY_EASY)

    def test_init_hard_difficulty(self) -> None:
        """Test initialization with hard difficulty."""
        controller = AIController(
            self.paddle, self.ball, AIController.DIFFICULTY_HARD
        )
        self.assertEqual(controller.difficulty, AIController.DIFFICULTY_HARD)

    def test_set_difficulty(self) -> None:
        """Test changing difficulty level."""
        controller = AIController(self.paddle, self.ball)
        controller.set_difficulty(AIController.DIFFICULTY_HARD)
        self.assertEqual(controller.difficulty, AIController.DIFFICULTY_HARD)

    def test_difficulty_settings_exist(self) -> None:
        """Test that all difficulty settings exist."""
        self.assertIn(AIController.DIFFICULTY_EASY, AIController.DIFFICULTY_SETTINGS)
        self.assertIn(AIController.DIFFICULTY_MEDIUM, AIController.DIFFICULTY_SETTINGS)
        self.assertIn(AIController.DIFFICULTY_HARD, AIController.DIFFICULTY_SETTINGS)

    def test_difficulty_settings_have_required_keys(self) -> None:
        """Test that difficulty settings have all required keys."""
        required_keys = ["reaction_delay", "speed", "accuracy", "prediction_error"]
        for difficulty in AIController.DIFFICULTY_SETTINGS.values():
            for key in required_keys:
                self.assertIn(key, difficulty)

    def test_clamp_position_within_bounds(self) -> None:
        """Test position clamping within boundaries."""
        controller = AIController(
            self.paddle, self.ball, paddle_config=self.paddle_config
        )
        # Position within bounds should not change
        result = controller._clamp_position(0.5)
        self.assertEqual(result, 0.5)

    def test_clamp_position_at_top(self) -> None:
        """Test position clamping at top boundary."""
        controller = AIController(
            self.paddle, self.ball, paddle_config=self.paddle_config
        )
        result = controller._clamp_position(1.0)
        self.assertLessEqual(result, 0.8)  # 1.0 - half_paddle (0.2)

    def test_clamp_position_at_bottom(self) -> None:
        """Test position clamping at bottom boundary."""
        controller = AIController(
            self.paddle, self.ball, paddle_config=self.paddle_config
        )
        result = controller._clamp_position(-1.0)
        self.assertGreaterEqual(result, -0.8)  # -1.0 + half_paddle (0.2)


if __name__ == "__main__":
    unittest.main()
