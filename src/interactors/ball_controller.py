"""Ball controller module for managing ball physics and collisions."""

import logging
from typing import Any, Dict, List, TYPE_CHECKING

import vtk

if TYPE_CHECKING:
    from src.interactors.score_manager import ScoreManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BallController:
    """
    Controller for managing ball movement, physics, and collision detection.

    Handles ball-paddle collisions, wall bounces, scoring, and speed increases.
    """

    # Default values
    DEFAULT_DIRECTION = [0.01, 0.01, 0.0]
    SUB_STEPS = 10  # Number of subdivisions for collision checks

    def __init__(
        self,
        actor: vtk.vtkActor,
        paddle1: vtk.vtkActor,
        paddle2: vtk.vtkActor,
        score_manager: "ScoreManager",
        game_config: Dict[str, Any],
    ) -> None:
        """
        Initialize the ball controller.

        Args:
            actor: The ball actor.
            paddle1: The left paddle actor.
            paddle2: The right paddle actor.
            score_manager: The score manager instance.
            game_config: The game configuration dictionary.
        """
        self.actor = actor
        self.paddle1 = paddle1
        self.paddle2 = paddle2
        self.score_manager = score_manager
        self.game_config = game_config
        self.direction: List[float] = self.DEFAULT_DIRECTION.copy()
        self.time_elapsed = 0
        self.paddle_x_length = self.game_config["paddle"]["x_length"]
        self.paddle_y_length = self.game_config["paddle"]["y_length"]
        self.ball_radius = self.game_config["ball"]["radius"]

    def reset(self) -> None:
        """Reset the ball to its initial position and direction."""
        self.actor.SetPosition(0, 0, 0)
        self.direction = self.DEFAULT_DIRECTION.copy()
        self.time_elapsed = 0
        logging.info("Ball reset to initial position and speed.")

    def execute(self) -> None:
        """Execute one frame of ball movement and collision detection."""
        self.time_elapsed += 1
        if self.time_elapsed % self.game_config["game"]["speed_increase_interval"] == 0:
            self.increase_ball_speed()

        for _ in range(self.SUB_STEPS):
            new_position = self.calculate_new_position(step_fraction=1 / self.SUB_STEPS)
            self.check_collisions(new_position)
            self.update_ball_position(new_position)

    def increase_ball_speed(self) -> None:
        """Increase ball speed according to the game configuration."""
        self.direction[0] *= self.game_config["game"]["speed_multiplier"]
        self.direction[1] *= self.game_config["game"]["speed_multiplier"]
        logging.debug(f"Ball speed increased. New direction: {self.direction}")

    def calculate_new_position(self, step_fraction: float) -> List[float]:
        """
        Calculate the new ball position based on current direction.

        Args:
            step_fraction: The fraction of a full step to move.

        Returns:
            The calculated new position as [x, y, z].
        """
        position = list(self.actor.GetPosition())
        new_position = [
            position[0] + self.direction[0] * step_fraction,
            position[1] + self.direction[1] * step_fraction,
            0,
        ]
        logging.debug(f"Calculated new ball position: {new_position}")
        return new_position

    def check_collisions(self, new_position: List[float]) -> None:
        """
        Check for all collisions and handle them.

        Args:
            new_position: The proposed new position to check.
        """
        self.check_paddle_collision(new_position)
        self.check_wall_collision(new_position)

    def check_paddle_collision(self, new_position: List[float]) -> None:
        """
        Check for paddle collisions and reverse ball direction if hit.

        Args:
            new_position: The proposed new position to check.
        """
        paddle1_pos = self.paddle1.GetPosition()
        paddle2_pos = self.paddle2.GetPosition()

        # Left paddle collision
        if (
            -0.9 <= new_position[0] - self.ball_radius <= -0.89
            and paddle1_pos[1] - self.paddle_y_length / 2
            <= new_position[1]
            <= paddle1_pos[1] + self.paddle_y_length / 2
            and self.direction[0] < 0
        ):
            self.direction[0] = -self.direction[0]
            overlap = -0.89 - (new_position[0] - self.ball_radius)
            new_position[0] += 2 * overlap  # Adjust position to avoid overlapping
            logging.debug("Ball hit left paddle.")

        # Right paddle collision
        elif (
            0.89 <= new_position[0] + self.ball_radius <= 0.9
            and paddle2_pos[1] - self.paddle_y_length / 2
            <= new_position[1]
            <= paddle2_pos[1] + self.paddle_y_length / 2
            and self.direction[0] > 0
        ):
            self.direction[0] = -self.direction[0]
            overlap = (new_position[0] + self.ball_radius) - 0.89
            new_position[0] -= 2 * overlap  # Adjust position to avoid overlapping
            logging.debug("Ball hit right paddle.")

    def check_wall_collision(self, new_position: List[float]) -> None:
        """
        Check for wall collisions, update scores, and bounce ball.

        Args:
            new_position: The proposed new position to check and modify.
        """
        if new_position[1] - self.ball_radius < -1.0:
            new_position[1] = -1.0 + self.ball_radius
            self.direction[1] = -self.direction[1]
            logging.debug("Ball hit bottom wall.")
        elif new_position[1] + self.ball_radius > 1.0:
            new_position[1] = 1.0 - self.ball_radius
            self.direction[1] = -self.direction[1]
            logging.debug("Ball hit top wall.")

        if new_position[0] - self.ball_radius < -1.0:
            new_position[0] = -1.0 + self.ball_radius
            self.direction[0] = -self.direction[0]
            self.score_manager.score_point(2)
            logging.info("Ball hit left wall. Player 2 scored.")
        elif new_position[0] + self.ball_radius > 1.0:
            new_position[0] = 1.0 - self.ball_radius
            self.direction[0] = -self.direction[0]
            self.score_manager.score_point(1)
            logging.info("Ball hit right wall. Player 1 scored.")

    def update_ball_position(self, new_position: List[float]) -> None:
        """
        Update the ball actor position.

        Args:
            new_position: The new position to set.
        """
        self.actor.SetPosition(new_position[0], new_position[1], 0)
        logging.debug(f"Ball position updated: {new_position}")
