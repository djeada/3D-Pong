"""Ball controller module for managing ball physics and collisions."""

import logging
import math
import random
from typing import Any, Callable, Dict, List, TYPE_CHECKING

import vtk

if TYPE_CHECKING:
    from src.interactors.score_manager import ScoreManager

logger = logging.getLogger(__name__)


class BallController:
    """
    Controller for managing ball movement, physics, and collision detection.

    Handles ball-paddle collisions with angle variation, wall bounces,
    scoring, speed increases, and visual feedback.
    """

    # Default values
    DEFAULT_DIRECTION = [0.01, 0.01, 0.0]
    SUB_STEPS = 10  # Number of subdivisions for collision checks
    MAX_ANGLE = math.pi / 3  # Maximum bounce angle (60 degrees)
    MIN_SPEED = 0.01
    MAX_SPEED = 0.08

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

        # Callbacks for events
        self.on_paddle_hit: Callable[[vtk.vtkActor], None] | None = None
        self.on_score: Callable[[int], None] | None = None
        self.on_wall_hit: Callable[[], None] | None = None

        # Rally counter
        self.rally_count = 0
        self.max_rally = 0

    def reset(self) -> None:
        """Reset the ball to its initial position and direction."""
        self.actor.SetPosition(0, 0, 0)
        # Randomize initial direction
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        direction_x = 0.01 if random.random() > 0.5 else -0.01
        self.direction = [direction_x, 0.01 * math.sin(angle), 0.0]
        self.time_elapsed = 0
        self.rally_count = 0
        logger.info("Ball reset to initial position with randomized direction.")

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
        logger.debug(f"Ball speed increased. New direction: {self.direction}")

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
        logger.debug(f"Calculated new ball position: {new_position}")
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
        Check for paddle collisions and apply angle-based bounce.

        The ball bounces at different angles depending on where it hits
        the paddle. Hitting near the edge creates a sharper angle.

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
            self._apply_paddle_bounce(new_position, paddle1_pos, is_left_paddle=True)
            self.rally_count += 1
            if self.on_paddle_hit:
                self.on_paddle_hit(self.paddle1)
            logger.debug(f"Ball hit left paddle. Rally count: {self.rally_count}")

        # Right paddle collision
        elif (
            0.89 <= new_position[0] + self.ball_radius <= 0.9
            and paddle2_pos[1] - self.paddle_y_length / 2
            <= new_position[1]
            <= paddle2_pos[1] + self.paddle_y_length / 2
            and self.direction[0] > 0
        ):
            self._apply_paddle_bounce(new_position, paddle2_pos, is_left_paddle=False)
            self.rally_count += 1
            if self.on_paddle_hit:
                self.on_paddle_hit(self.paddle2)
            logger.debug(f"Ball hit right paddle. Rally count: {self.rally_count}")

    def _apply_paddle_bounce(
        self, new_position: List[float], paddle_pos: tuple, is_left_paddle: bool
    ) -> None:
        """
        Apply angle-based bounce when ball hits paddle.

        Args:
            new_position: Ball position to adjust.
            paddle_pos: Position of the paddle that was hit.
            is_left_paddle: True if left paddle, False if right.
        """
        # Calculate hit position relative to paddle center (-1 to 1)
        relative_hit = (new_position[1] - paddle_pos[1]) / (self.paddle_y_length / 2)
        relative_hit = max(-1, min(1, relative_hit))  # Clamp to [-1, 1]

        # Calculate bounce angle based on hit position
        bounce_angle = relative_hit * self.MAX_ANGLE

        # Calculate current speed
        current_speed = math.sqrt(self.direction[0] ** 2 + self.direction[1] ** 2)
        current_speed = min(current_speed, self.MAX_SPEED)

        # Apply new direction based on angle
        if is_left_paddle:
            self.direction[0] = current_speed * math.cos(bounce_angle)
            overlap = -0.89 - (new_position[0] - self.ball_radius)
            new_position[0] += 2 * overlap
        else:
            self.direction[0] = -current_speed * math.cos(bounce_angle)
            overlap = (new_position[0] + self.ball_radius) - 0.89
            new_position[0] -= 2 * overlap

        self.direction[1] = current_speed * math.sin(bounce_angle)

    def get_speed(self) -> float:
        """
        Get current ball speed magnitude.

        Returns:
            Current speed as a float.
        """
        return math.sqrt(self.direction[0] ** 2 + self.direction[1] ** 2)

    def check_wall_collision(self, new_position: List[float]) -> None:
        """
        Check for wall collisions, update scores, and bounce ball.

        Args:
            new_position: The proposed new position to check and modify.
        """
        if new_position[1] - self.ball_radius < -1.0:
            new_position[1] = -1.0 + self.ball_radius
            self.direction[1] = -self.direction[1]
            if self.on_wall_hit:
                self.on_wall_hit()
            logger.debug("Ball hit bottom wall.")
        elif new_position[1] + self.ball_radius > 1.0:
            new_position[1] = 1.0 - self.ball_radius
            self.direction[1] = -self.direction[1]
            if self.on_wall_hit:
                self.on_wall_hit()
            logger.debug("Ball hit top wall.")

        if new_position[0] - self.ball_radius < -1.0:
            new_position[0] = -1.0 + self.ball_radius
            self.direction[0] = -self.direction[0]
            self._handle_score(2)
            logger.info("Ball hit left wall. Player 2 scored.")
        elif new_position[0] + self.ball_radius > 1.0:
            new_position[0] = 1.0 - self.ball_radius
            self.direction[0] = -self.direction[0]
            self._handle_score(1)
            logger.info("Ball hit right wall. Player 1 scored.")

    def _handle_score(self, player: int) -> None:
        """
        Handle scoring and update rally statistics.

        Args:
            player: Player who scored.
        """
        if self.rally_count > self.max_rally:
            self.max_rally = self.rally_count
        self.rally_count = 0
        self.score_manager.score_point(player)
        if self.on_score:
            self.on_score(player)

    def update_ball_position(self, new_position: List[float]) -> None:
        """
        Update the ball actor position.

        Args:
            new_position: The new position to set.
        """
        self.actor.SetPosition(new_position[0], new_position[1], 0)
        logger.debug(f"Ball position updated: {new_position}")
