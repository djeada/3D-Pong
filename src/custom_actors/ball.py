"""Ball actor module for creating the futuristic neon game ball."""

from typing import Any, Dict

import vtk


def create_ball(config: Dict[str, Any]) -> vtk.vtkActor:
    """
    Create a futuristic glowing ball actor for the game.

    Args:
        config: Ball configuration containing radius, phi_resolution,
                and theta_resolution values.

    Returns:
        A VTK actor representing the neon-style ball.
    """
    # Slightly larger ball for better visibility
    radius = config.get("radius", 0.02) * 1.5
    
    ball_source = vtk.vtkSphereSource()
    ball_source.SetRadius(radius)
    ball_source.SetPhiResolution(config.get("phi_resolution", 20) + 10)  # Smoother
    ball_source.SetThetaResolution(config.get("theta_resolution", 20) + 10)

    ball_mapper = vtk.vtkPolyDataMapper()
    ball_mapper.SetInputConnection(ball_source.GetOutputPort())

    ball_actor = vtk.vtkActor()
    ball_actor.SetMapper(ball_mapper)
    
    # Neon glow material properties
    prop = ball_actor.GetProperty()
    prop.SetColor(1.0, 1.0, 1.0)  # Start white, will be colored by effects
    prop.SetAmbient(0.5)  # High ambient for glow effect
    prop.SetDiffuse(0.5)
    prop.SetSpecular(1.0)
    prop.SetSpecularPower(80)
    prop.SetInterpolationToPhong()

    return ball_actor
