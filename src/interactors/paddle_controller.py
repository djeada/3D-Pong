"""Paddle controller module for handling paddle movement."""

import logging
from typing import Any, Dict

import vtk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PaddleController:
    """Controller for managing paddle movement and boundary constraints."""

    # Default boundary values (can be overridden via config)
    BOUNDARY_TOP = 1.0
    BOUNDARY_BOTTOM = -1.0
    MOVE_SPEED = 0.1

    def __init__(
        self,
        paddle1: vtk.vtkActor,
        paddle2: vtk.vtkActor,
        paddle_config: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the paddle controller.

        Args:
            paddle1: The left paddle actor.
            paddle2: The right paddle actor.
            paddle_config: Optional configuration for paddle dimensions.
        """
        self.paddle1 = paddle1
        self.paddle2 = paddle2
        self.paddle_y_length = (
            paddle_config.get("y_length", 0.4) if paddle_config else 0.4
        )

    def move_paddles(self, key: str) -> None:
        """
        Move paddles based on key input with boundary constraints.

        Args:
            key: The key pressed by the user.
        """
        position_left_paddle = list(self.paddle1.GetPosition())
        position_right_paddle = list(self.paddle2.GetPosition())

        if key == "Up":
            position_right_paddle[1] = self._clamp_position(
                position_right_paddle[1] + self.MOVE_SPEED
            )
        elif key == "Down":
            position_right_paddle[1] = self._clamp_position(
                position_right_paddle[1] - self.MOVE_SPEED
            )
        elif key == "w":
            position_left_paddle[1] = self._clamp_position(
                position_left_paddle[1] + self.MOVE_SPEED
            )
        elif key == "s":
            position_left_paddle[1] = self._clamp_position(
                position_left_paddle[1] - self.MOVE_SPEED
            )

        self.paddle1.SetPosition(position_left_paddle[0], position_left_paddle[1], 0)
        self.paddle2.SetPosition(position_right_paddle[0], position_right_paddle[1], 0)
        logging.debug(
            f"Paddle positions updated. Left: {position_left_paddle}, Right: {position_right_paddle}"
        )

    def _clamp_position(self, y_position: float) -> float:
        """
        Clamp paddle position to stay within boundaries.

        Args:
            y_position: The desired Y position.

        Returns:
            The clamped Y position within valid boundaries.
        """
        half_paddle = self.paddle_y_length / 2
        min_y = self.BOUNDARY_BOTTOM + half_paddle
        max_y = self.BOUNDARY_TOP - half_paddle
        return max(min_y, min(max_y, y_position))

    def reset_positions(self) -> None:
        """Reset both paddles to their initial centered positions."""
        left_x = self.paddle1.GetPosition()[0]
        right_x = self.paddle2.GetPosition()[0]
        self.paddle1.SetPosition(left_x, 0, 0)
        self.paddle2.SetPosition(right_x, 0, 0)
        logging.debug("Paddle positions reset to center.")
