"""Ball actor module for creating the futuristic neon game ball."""

from typing import Any, Dict

import vtk

# Ball configuration constants
BALL_SIZE_MULTIPLIER = 1.5  # Scale factor for visibility
MIN_RESOLUTION = 20
MAX_RESOLUTION = 50  # Cap for performance


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
    radius = config.get("radius", 0.02) * BALL_SIZE_MULTIPLIER

    # Smoother ball with capped resolution for performance
    phi_res = min(config.get("phi_resolution", MIN_RESOLUTION) + 10, MAX_RESOLUTION)
    theta_res = min(config.get("theta_resolution", MIN_RESOLUTION) + 10, MAX_RESOLUTION)

    ball_source = vtk.vtkSphereSource()
    ball_source.SetRadius(radius)
    ball_source.SetPhiResolution(phi_res)
    ball_source.SetThetaResolution(theta_res)

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
