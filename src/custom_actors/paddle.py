"""Paddle actor module for creating game paddles."""

from typing import Any, Dict

import vtk


def create_paddle(config: Dict[str, Any]) -> vtk.vtkActor:
    """
    Create a paddle actor for the game.

    Args:
        config: Paddle configuration containing x_length, y_length,
                and z_length values.

    Returns:
        A VTK actor representing the paddle.
    """
    paddle_source = vtk.vtkCubeSource()
    paddle_source.SetXLength(config["x_length"])
    paddle_source.SetYLength(config["y_length"])
    paddle_source.SetZLength(config["z_length"])

    paddle_mapper = vtk.vtkPolyDataMapper()
    paddle_mapper.SetInputConnection(paddle_source.GetOutputPort())

    paddle_actor = vtk.vtkActor()
    paddle_actor.SetMapper(paddle_mapper)

    return paddle_actor
