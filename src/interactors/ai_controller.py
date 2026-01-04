"""AI controller module for computer-controlled paddle."""

import logging
import random
from typing import Any, Dict

import vtk

logger = logging.getLogger(__name__)


class AIController:
    """
    AI controller for computer-controlled paddle.

    Provides three difficulty levels with varying reaction times and accuracy.
    """

    # Difficulty presets
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"

    DIFFICULTY_SETTINGS = {
        DIFFICULTY_EASY: {
            "reaction_delay": 15,  # Frames before AI reacts
            "speed": 0.03,  # Movement speed
            "accuracy": 0.7,  # Chance to move correctly
            "prediction_error": 0.15,  # Random offset in prediction
        },
        DIFFICULTY_MEDIUM: {
            "reaction_delay": 8,
            "speed": 0.05,
            "accuracy": 0.85,
            "prediction_error": 0.08,
        },
        DIFFICULTY_HARD: {
            "reaction_delay": 3,
            "speed": 0.08,
            "accuracy": 0.95,
            "prediction_error": 0.03,
        },
    }

    def __init__(
        self,
        paddle: vtk.vtkActor,
        ball: vtk.vtkActor,
        difficulty: str = DIFFICULTY_MEDIUM,
        paddle_config: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the AI controller.

        Args:
            paddle: The paddle actor controlled by AI.
            ball: The ball actor to track.
            difficulty: AI difficulty level ("easy", "medium", "hard").
            paddle_config: Optional paddle configuration.
        """
        self.paddle = paddle
        self.ball = ball
        self.difficulty = difficulty
        self.settings = self.DIFFICULTY_SETTINGS.get(
            difficulty, self.DIFFICULTY_SETTINGS[self.DIFFICULTY_MEDIUM]
        )
        self.paddle_y_length = (
            paddle_config.get("y_length", 0.4) if paddle_config else 0.4
        )
        self.frame_counter = 0
        self.target_y = 0.0
        self.prediction_offset = 0.0

        # Boundary constraints
        self.boundary_top = 1.0
        self.boundary_bottom = -1.0

        logger.info(f"AI Controller initialized with difficulty: {difficulty}")

    def update(self, ball_direction: list) -> None:
        """
        Update AI paddle position based on ball position.

        Args:
            ball_direction: Current ball direction [dx, dy, dz].
        """
        self.frame_counter += 1

        # Only react after delay
        if self.frame_counter % self.settings["reaction_delay"] != 0:
            return

        ball_pos = self.ball.GetPosition()
        paddle_pos = list(self.paddle.GetPosition())

        # Only track ball when it's coming toward AI paddle (right side)
        if ball_direction[0] > 0:
            # Predict where ball will be
            self._calculate_target(ball_pos, ball_direction)

            # Apply accuracy check
            if random.random() < self.settings["accuracy"]:
                self._move_toward_target(paddle_pos)
        else:
            # Return to center when ball is going away
            self._move_toward_center(paddle_pos)

    def _calculate_target(self, ball_pos: tuple, ball_direction: list) -> None:
        """Calculate target Y position with prediction error."""
        # Predict ball Y when it reaches paddle X
        paddle_x = self.paddle.GetPosition()[0]
        time_to_reach = (paddle_x - ball_pos[0]) / ball_direction[0] if ball_direction[0] != 0 else 0

        predicted_y = ball_pos[1] + ball_direction[1] * time_to_reach

        # Account for wall bounces
        while predicted_y < -1.0 or predicted_y > 1.0:
            if predicted_y < -1.0:
                predicted_y = -2.0 - predicted_y
            elif predicted_y > 1.0:
                predicted_y = 2.0 - predicted_y

        # Add prediction error
        self.prediction_offset = (random.random() - 0.5) * 2 * self.settings["prediction_error"]
        self.target_y = predicted_y + self.prediction_offset

    def _move_toward_target(self, paddle_pos: list) -> None:
        """Move paddle toward target position."""
        diff = self.target_y - paddle_pos[1]
        speed = self.settings["speed"]

        if abs(diff) > speed:
            new_y = paddle_pos[1] + (speed if diff > 0 else -speed)
        else:
            new_y = self.target_y

        new_y = self._clamp_position(new_y)
        self.paddle.SetPosition(paddle_pos[0], new_y, 0)

    def _move_toward_center(self, paddle_pos: list) -> None:
        """Move paddle toward center position."""
        speed = self.settings["speed"] * 0.5  # Slower return to center
        diff = 0 - paddle_pos[1]

        if abs(diff) > speed:
            new_y = paddle_pos[1] + (speed if diff > 0 else -speed)
        else:
            new_y = 0

        new_y = self._clamp_position(new_y)
        self.paddle.SetPosition(paddle_pos[0], new_y, 0)

    def _clamp_position(self, y_position: float) -> float:
        """Clamp paddle position to stay within boundaries."""
        half_paddle = self.paddle_y_length / 2
        min_y = self.boundary_bottom + half_paddle
        max_y = self.boundary_top - half_paddle
        return max(min_y, min(max_y, y_position))

    def set_difficulty(self, difficulty: str) -> None:
        """
        Change AI difficulty level.

        Args:
            difficulty: New difficulty level.
        """
        if difficulty in self.DIFFICULTY_SETTINGS:
            self.difficulty = difficulty
            self.settings = self.DIFFICULTY_SETTINGS[difficulty]
            logger.info(f"AI difficulty changed to: {difficulty}")
