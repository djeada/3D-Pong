"""Interactor module for handling game input and timer events."""

import logging
from typing import Any, Dict

import vtk

from src.interactors.ball_controller import BallController
from src.interactors.paddle_controller import PaddleController
from src.interactors.score_manager import ScoreManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    Custom interactor style for handling keyboard input and game logic.

    This class manages the game state, including pause/resume functionality,
    game reset, and input handling for paddle movement.
    """

    def __init__(
        self,
        actor: vtk.vtkActor,
        renderer: vtk.vtkRenderer,
        paddle1: vtk.vtkActor,
        paddle2: vtk.vtkActor,
        score1: vtk.vtkTextActor,
        score2: vtk.vtkTextActor,
        game_config: Dict[str, Any],
    ) -> None:
        """
        Initialize the interactor style.

        Args:
            actor: The ball actor.
            renderer: The VTK renderer.
            paddle1: The left paddle actor.
            paddle2: The right paddle actor.
            score1: The score text actor for player 1.
            score2: The score text actor for player 2.
            game_config: The game configuration dictionary.
        """
        super().__init__()
        self.renderer = renderer
        self.game_config = game_config
        self.paused = False

        self.paddle_controller = PaddleController(
            paddle1, paddle2, game_config.get("paddle")
        )
        self.score_manager = ScoreManager(score1, score2)
        self.ball_controller = BallController(
            actor, paddle1, paddle2, self.score_manager, game_config
        )
        self.timer_id = None
        self.AddObserver("KeyPressEvent", self.key_press_event)
        logging.info("KeyPressInteractorStyle initialized.")

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.ball_controller.reset()
        self.paddle_controller.reset_positions()
        self.score_manager.reset()
        self.paused = False
        logging.info("Game reset. Ball position, paddles, and scores reset.")

    def toggle_pause(self) -> None:
        """Toggle the game pause state."""
        self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        logging.info(f"Game {state}.")

    def key_press_event(self, obj: vtk.vtkObject, event: str) -> None:
        """
        Handle key press events.

        Args:
            obj: The VTK object that triggered the event.
            event: The event type string.
        """
        key = self.GetInteractor().GetKeySym()
        logging.debug(f"Key pressed: {key}")

        if key == "space":
            self.toggle_pause()
        elif key == "r" or key == "R":
            self.reset()
        elif not self.paused:
            self.paddle_controller.move_paddles(key)

    def execute(self, obj: vtk.vtkObject, event: str) -> None:
        """
        Execute the game loop update.

        Args:
            obj: The VTK object that triggered the event.
            event: The event type string.
        """
        if not self.paused:
            self.ball_controller.execute()
        self.GetInteractor().GetRenderWindow().Render()
