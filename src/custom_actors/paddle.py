"""Paddle actor module for creating futuristic neon game paddles."""

from typing import Any, Dict

import vtk


def create_paddle(config: Dict[str, Any]) -> vtk.vtkActor:
    """
    Create a futuristic glowing paddle actor for the game.

    Args:
        config: Paddle configuration containing x_length, y_length,
                and z_length values.

    Returns:
        A VTK actor representing the neon-style paddle.
    """
    # Use rounded cylinder for futuristic look
    # Create a rounded paddle using a cylinder
    paddle_source = vtk.vtkCylinderSource()
    paddle_source.SetHeight(config.get("y_length", 0.4))
    paddle_source.SetRadius(config.get("x_length", 0.02) * 1.5)
    paddle_source.SetResolution(16)

    # Rotate cylinder to be vertical
    transform = vtk.vtkTransform()
    transform.RotateX(0)  # Cylinder is already vertical

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(paddle_source.GetOutputPort())
    transform_filter.SetTransform(transform)

    paddle_mapper = vtk.vtkPolyDataMapper()
    paddle_mapper.SetInputConnection(transform_filter.GetOutputPort())

    paddle_actor = vtk.vtkActor()
    paddle_actor.SetMapper(paddle_mapper)

    # Neon glow material properties
    prop = paddle_actor.GetProperty()
    prop.SetAmbient(0.4)  # Higher ambient for glow effect
    prop.SetDiffuse(0.6)
    prop.SetSpecular(0.9)
    prop.SetSpecularPower(60)
    prop.SetInterpolationToPhong()

    return paddle_actor
