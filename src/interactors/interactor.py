import logging
from typing import Any, Dict, List

import vtk

from src.interactors.ball_controller import BallController
from src.interactors.paddle_controller import PaddleController
from src.interactors.score_manager import ScoreManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
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
        super().__init__()
        self.renderer = renderer
        self.paddle_controller = PaddleController(paddle1, paddle2)
        self.score_manager = ScoreManager(score1, score2)
        self.ball_controller = BallController(
            actor, paddle1, paddle2, self.score_manager, game_config
        )
        self.timer_id = None
        self.AddObserver("KeyPressEvent", self.key_press_event)
        logging.info("KeyPressInteractorStyle initialized.")

    def reset(self) -> None:
        self.ball_controller.actor.SetPosition(0, 0, 0)
        self.score_manager.score = [0, 0]
        self.score_manager.update_score_display()
        logging.info("Game reset. Ball position and scores reset.")

    def key_press_event(self, obj: vtk.vtkObject, event: str) -> None:
        key = self.GetInteractor().GetKeySym()
        logging.debug(f"Key pressed: {key}")
        self.paddle_controller.move_paddles(key)

    def execute(self, obj: vtk.vtkObject, event: str) -> None:
        self.ball_controller.execute()
        self.GetInteractor().GetRenderWindow().Render()
