"""Ball actor module for creating the game ball."""

from typing import Any, Dict

import vtk


def create_ball(config: Dict[str, Any]) -> vtk.vtkActor:
    """
    Create a ball actor for the game.

    Args:
        config: Ball configuration containing radius, phi_resolution,
                and theta_resolution values.

    Returns:
        A VTK actor representing the ball.
    """
    ball_source = vtk.vtkSphereSource()
    ball_source.SetRadius(config["radius"])
    ball_source.SetPhiResolution(config["phi_resolution"])
    ball_source.SetThetaResolution(config["theta_resolution"])

    ball_mapper = vtk.vtkPolyDataMapper()
    ball_mapper.SetInputConnection(ball_source.GetOutputPort())

    ball_actor = vtk.vtkActor()
    ball_actor.SetMapper(ball_mapper)

    return ball_actor
