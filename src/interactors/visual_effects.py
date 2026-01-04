"""Visual effects module for game visual feedback."""

import logging
from typing import List, Tuple

import vtk

logger = logging.getLogger(__name__)


class VisualEffects:
    """
    Manager for visual effects in the game.

    Handles color changes, flash effects, and ball trail rendering.
    """

    # Color presets
    COLOR_WHITE = (1.0, 1.0, 1.0)
    COLOR_RED = (1.0, 0.2, 0.2)
    COLOR_BLUE = (0.2, 0.4, 1.0)
    COLOR_GREEN = (0.2, 1.0, 0.4)
    COLOR_YELLOW = (1.0, 1.0, 0.2)
    COLOR_ORANGE = (1.0, 0.5, 0.0)
    COLOR_CYAN = (0.0, 1.0, 1.0)

    def __init__(self, renderer: vtk.vtkRenderer) -> None:
        """
        Initialize the visual effects manager.

        Args:
            renderer: The VTK renderer for adding effects.
        """
        self.renderer = renderer
        self.flash_duration = 0
        self.flash_actor: vtk.vtkActor | None = None
        self.trail_actors: List[vtk.vtkActor] = []
        self.max_trail_length = 15
        self.trail_enabled = True

        # Store original colors
        self.original_colors: dict = {}

        logger.info("Visual effects manager initialized.")

    def flash_score(self, player: int) -> None:
        """
        Create a flash effect when a player scores.

        Args:
            player: Player number (1 or 2) who scored.
        """
        color = self.COLOR_BLUE if player == 1 else self.COLOR_RED
        self.flash_duration = 10
        self.renderer.SetBackground(*color)
        logger.debug(f"Score flash triggered for player {player}")

    def update_flash(self) -> None:
        """Update flash effect countdown and reset background."""
        if self.flash_duration > 0:
            self.flash_duration -= 1
            if self.flash_duration == 0:
                self.renderer.SetBackground(0.1, 0.1, 0.15)  # Dark background

    def set_ball_color(self, ball: vtk.vtkActor, color: Tuple[float, float, float]) -> None:
        """
        Set the ball color.

        Args:
            ball: The ball actor.
            color: RGB color tuple (0.0-1.0 for each component).
        """
        ball.GetProperty().SetColor(*color)

    def set_paddle_color(self, paddle: vtk.vtkActor, color: Tuple[float, float, float]) -> None:
        """
        Set a paddle color.

        Args:
            paddle: The paddle actor.
            color: RGB color tuple.
        """
        paddle.GetProperty().SetColor(*color)

    def paddle_hit_effect(self, paddle: vtk.vtkActor, ball: vtk.vtkActor) -> None:
        """
        Apply visual effect when paddle hits ball.

        Args:
            paddle: The paddle that hit the ball.
            ball: The ball actor.
        """
        # Briefly change colors
        self.set_paddle_color(paddle, self.COLOR_YELLOW)
        self.set_ball_color(ball, self.COLOR_ORANGE)

    def reset_colors(self, ball: vtk.vtkActor, paddle1: vtk.vtkActor, paddle2: vtk.vtkActor) -> None:
        """
        Reset all game object colors to defaults.

        Args:
            ball: The ball actor.
            paddle1: First paddle actor.
            paddle2: Second paddle actor.
        """
        self.set_ball_color(ball, self.COLOR_WHITE)
        self.set_paddle_color(paddle1, self.COLOR_CYAN)
        self.set_paddle_color(paddle2, self.COLOR_GREEN)

    def update_ball_trail(self, ball: vtk.vtkActor) -> None:
        """
        Update the ball trail effect.

        Args:
            ball: The ball actor to trail.
        """
        if not self.trail_enabled:
            return

        ball_pos = ball.GetPosition()

        # Create trail sphere
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(0.015)  # Slightly smaller than ball
        sphere.SetPhiResolution(8)
        sphere.SetThetaResolution(8)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        trail_actor = vtk.vtkActor()
        trail_actor.SetMapper(mapper)
        trail_actor.SetPosition(ball_pos[0], ball_pos[1], ball_pos[2])

        # Fade color based on position in trail
        alpha = 0.6
        trail_actor.GetProperty().SetOpacity(alpha)
        trail_actor.GetProperty().SetColor(0.5, 0.5, 0.8)

        self.trail_actors.append(trail_actor)
        self.renderer.AddActor(trail_actor)

        # Remove old trail segments
        while len(self.trail_actors) > self.max_trail_length:
            old_actor = self.trail_actors.pop(0)
            self.renderer.RemoveActor(old_actor)

        # Update opacity of existing trail
        for i, actor in enumerate(self.trail_actors):
            opacity = (i + 1) / len(self.trail_actors) * 0.4
            actor.GetProperty().SetOpacity(opacity)

    def clear_trail(self) -> None:
        """Clear all trail actors."""
        for actor in self.trail_actors:
            self.renderer.RemoveActor(actor)
        self.trail_actors.clear()

    def toggle_trail(self) -> bool:
        """
        Toggle trail effect on/off.

        Returns:
            Current trail enabled state.
        """
        self.trail_enabled = not self.trail_enabled
        if not self.trail_enabled:
            self.clear_trail()
        logger.info(f"Trail effect {'enabled' if self.trail_enabled else 'disabled'}")
        return self.trail_enabled

    def set_dark_theme(self) -> None:
        """Apply dark theme to the renderer."""
        self.renderer.SetBackground(0.1, 0.1, 0.15)
        logger.debug("Dark theme applied")

    def apply_speed_color(self, ball: vtk.vtkActor, speed: float) -> None:
        """
        Change ball color based on speed.

        Args:
            ball: The ball actor.
            speed: Current ball speed magnitude.
        """
        # Interpolate from white to red based on speed
        normalized_speed = min(speed / 0.05, 1.0)  # Normalize to 0-1
        r = 1.0
        g = 1.0 - normalized_speed * 0.7
        b = 1.0 - normalized_speed * 0.7
        self.set_ball_color(ball, (r, g, b))
