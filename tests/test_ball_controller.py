"""Unit tests for BallController."""

import math
import unittest
from unittest.mock import MagicMock

from src.interactors.ball_controller import BallController


class TestBallController(unittest.TestCase):
    """Tests for the BallController class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.actor = MagicMock()
        self.paddle1 = MagicMock()
        self.paddle2 = MagicMock()
        self.score_manager = MagicMock()

        self.actor.GetPosition.return_value = (0, 0, 0)
        self.paddle1.GetPosition.return_value = (-0.9, 0, 0)
        self.paddle2.GetPosition.return_value = (0.9, 0, 0)

        self.game_config = {
            "ball": {"radius": 0.02, "phi_resolution": 20, "theta_resolution": 20},
            "paddle": {"x_length": 0.02, "y_length": 0.4, "z_length": 0.02},
            "game": {"speed_increase_interval": 500, "speed_multiplier": 1.1},
        }

        self.controller = BallController(
            self.actor,
            self.paddle1,
            self.paddle2,
            self.score_manager,
            self.game_config,
        )

    def test_initial_direction(self) -> None:
        """Test that initial direction magnitude is set correctly."""
        # Initial direction has x=0.01, y=0.01, so speed is sqrt(0.0001+0.0001) ≈ 0.0141
        speed = math.sqrt(self.controller.direction[0] ** 2 + self.controller.direction[1] ** 2)
        self.assertAlmostEqual(speed, 0.0141, places=3)

    def test_reset_ball(self) -> None:
        """Test resetting ball to initial state."""
        self.controller.direction = [0.05, 0.05, 0.0]
        self.controller.time_elapsed = 100
        self.controller.rally_count = 5
        self.controller.reset()

        self.actor.SetPosition.assert_called_with(0, 0, 0)
        self.assertEqual(self.controller.time_elapsed, 0)
        self.assertEqual(self.controller.rally_count, 0)
        # Direction is now randomized, so check magnitude instead
        self.assertAlmostEqual(abs(self.controller.direction[0]), 0.01, places=3)

    def test_ball_radius_from_config(self) -> None:
        """Test that ball radius is taken from config."""
        self.assertEqual(self.controller.ball_radius, 0.02)

    def test_calculate_new_position(self) -> None:
        """Test calculating new position based on direction."""
        new_pos = self.controller.calculate_new_position(step_fraction=1.0)
        self.assertAlmostEqual(new_pos[0], 0.01)
        self.assertAlmostEqual(new_pos[1], 0.01)

    def test_increase_ball_speed(self) -> None:
        """Test that ball speed increases correctly."""
        initial_x = self.controller.direction[0]
        initial_y = self.controller.direction[1]
        self.controller.increase_ball_speed()

        self.assertAlmostEqual(self.controller.direction[0], initial_x * 1.1)
        self.assertAlmostEqual(self.controller.direction[1], initial_y * 1.1)


if __name__ == "__main__":
    unittest.main()
