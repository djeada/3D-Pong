import vtk
from typing import Tuple


def create_text_actor(position: Tuple[int, int]) -> vtk.vtkTextActor:
    text_actor = vtk.vtkTextActor()
    text_actor.SetPosition(*position)
    text_property = text_actor.GetTextProperty()
    text_property.SetFontSize(24)
    text_property.BoldOn()
    text_actor.SetInput("0")

    return text_actor
