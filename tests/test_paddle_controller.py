"""Unit tests for PaddleController."""

import unittest
from unittest.mock import MagicMock

from src.interactors.paddle_controller import PaddleController


class TestPaddleController(unittest.TestCase):
    """Tests for the PaddleController class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.paddle1 = MagicMock()
        self.paddle2 = MagicMock()
        self.paddle1.GetPosition.return_value = (-0.9, 0, 0)
        self.paddle2.GetPosition.return_value = (0.9, 0, 0)
        self.controller = PaddleController(self.paddle1, self.paddle2)

    def test_move_paddle1_up(self) -> None:
        """Test moving paddle 1 up with 'w' key."""
        self.controller.move_paddles("w")
        self.paddle1.SetPosition.assert_called()
        call_args = self.paddle1.SetPosition.call_args[0]
        self.assertAlmostEqual(call_args[1], 0.1)

    def test_move_paddle1_down(self) -> None:
        """Test moving paddle 1 down with 's' key."""
        self.controller.move_paddles("s")
        self.paddle1.SetPosition.assert_called()
        call_args = self.paddle1.SetPosition.call_args[0]
        self.assertAlmostEqual(call_args[1], -0.1)

    def test_move_paddle2_up(self) -> None:
        """Test moving paddle 2 up with 'Up' key."""
        self.controller.move_paddles("Up")
        self.paddle2.SetPosition.assert_called()
        call_args = self.paddle2.SetPosition.call_args[0]
        self.assertAlmostEqual(call_args[1], 0.1)

    def test_move_paddle2_down(self) -> None:
        """Test moving paddle 2 down with 'Down' key."""
        self.controller.move_paddles("Down")
        self.paddle2.SetPosition.assert_called()
        call_args = self.paddle2.SetPosition.call_args[0]
        self.assertAlmostEqual(call_args[1], -0.1)

    def test_boundary_constraint_top(self) -> None:
        """Test that paddle stays within top boundary."""
        self.paddle1.GetPosition.return_value = (-0.9, 0.7, 0)
        self.controller.move_paddles("w")
        call_args = self.paddle1.SetPosition.call_args[0]
        # With paddle y_length of 0.4, max y is 0.8 (1.0 - 0.2)
        self.assertLessEqual(call_args[1], 0.8)

    def test_boundary_constraint_bottom(self) -> None:
        """Test that paddle stays within bottom boundary."""
        self.paddle1.GetPosition.return_value = (-0.9, -0.7, 0)
        self.controller.move_paddles("s")
        call_args = self.paddle1.SetPosition.call_args[0]
        # With paddle y_length of 0.4, min y is -0.8 (-1.0 + 0.2)
        self.assertGreaterEqual(call_args[1], -0.8)

    def test_reset_positions(self) -> None:
        """Test resetting paddle positions to center."""
        self.controller.reset_positions()
        call_args1 = self.paddle1.SetPosition.call_args[0]
        call_args2 = self.paddle2.SetPosition.call_args[0]
        self.assertEqual(call_args1[1], 0)
        self.assertEqual(call_args2[1], 0)

    def test_unknown_key_does_not_crash(self) -> None:
        """Test that unknown keys don't crash the game."""
        # These should not raise any exceptions
        self.controller.move_paddles("x")
        self.controller.move_paddles("Space")
        self.controller.move_paddles("Shift_L")
        self.controller.move_paddles("Control_L")
        self.controller.move_paddles("1")
        self.controller.move_paddles("F1")


if __name__ == "__main__":
    unittest.main()
