import logging

import vtk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PaddleController:
    def __init__(self, paddle1: vtk.vtkActor, paddle2: vtk.vtkActor) -> None:
        self.paddle1 = paddle1
        self.paddle2 = paddle2

    def move_paddles(self, key: str) -> None:
        position_left_paddle = list(self.paddle1.GetPosition())
        position_right_paddle = list(self.paddle2.GetPosition())

        if key == "Up":
            position_right_paddle[1] += 0.1
        elif key == "Down":
            position_right_paddle[1] -= 0.1
        elif key == "w":
            position_left_paddle[1] += 0.1
        elif key == "s":
            position_left_paddle[1] -= 0.1

        self.paddle1.SetPosition(position_left_paddle[0], position_left_paddle[1], 0)
        self.paddle2.SetPosition(position_right_paddle[0], position_right_paddle[1], 0)
        logging.debug(
            f"Paddle positions updated. Left: {position_left_paddle}, Right: {position_right_paddle}"
        )
