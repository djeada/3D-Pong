"""Score text actor module for displaying player scores."""

from typing import Tuple

import vtk


def create_text_actor(position: Tuple[int, int]) -> vtk.vtkTextActor:
    """
    Create a text actor for displaying a score.

    Args:
        position: The screen position (x, y) for the text actor.

    Returns:
        A VTK text actor configured for score display.
    """
    text_actor = vtk.vtkTextActor()
    text_actor.SetPosition(*position)
    text_property = text_actor.GetTextProperty()
    text_property.SetFontSize(24)
    text_property.BoldOn()
    text_actor.SetInput("0")

    return text_actor
