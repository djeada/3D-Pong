"""Border actor module for creating futuristic neon game boundaries."""

from typing import Tuple

import vtk


def create_border(
    point1: Tuple[float, float, float], point2: Tuple[float, float, float]
) -> vtk.vtkActor:
    """
    Create a futuristic neon border line actor between two points.

    Args:
        point1: The starting point coordinates (x, y, z).
        point2: The ending point coordinates (x, y, z).

    Returns:
        A VTK actor representing the neon border line.
    """
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(*point1)
    line_source.SetPoint2(*point2)

    # Use tube filter for thicker, glowing lines
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(line_source.GetOutputPort())
    tube_filter.SetRadius(0.008)  # Thicker border
    tube_filter.SetNumberOfSides(8)

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputConnection(tube_filter.GetOutputPort())

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)
    
    # Neon purple color with glow effect
    prop = line_actor.GetProperty()
    prop.SetColor(0.6, 0.0, 1.0)  # Neon purple
    prop.SetAmbient(0.6)  # Higher ambient for glow
    prop.SetDiffuse(0.4)
    prop.SetSpecular(0.8)
    prop.SetSpecularPower(50)

    return line_actor
