"""Interactors module for game input and controllers."""

from src.interactors.ball_controller import BallController
from src.interactors.interactor import KeyPressInteractorStyle
from src.interactors.paddle_controller import PaddleController
from src.interactors.score_manager import ScoreManager

__all__ = [
    "BallController",
    "PaddleController",
    "ScoreManager",
    "KeyPressInteractorStyle",
]
