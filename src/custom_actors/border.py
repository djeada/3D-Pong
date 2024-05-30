from typing import Tuple

import vtk


def create_border(
    point1: Tuple[float, float, float], point2: Tuple[float, float, float]
) -> vtk.vtkActor:
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(*point1)
    line_source.SetPoint2(*point2)

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputConnection(line_source.GetOutputPort())

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)

    return line_actor
