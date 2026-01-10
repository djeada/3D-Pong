"""Score text actor module for displaying player scores with futuristic neon styling."""

from typing import Tuple

import vtk


def create_text_actor(position: Tuple[int, int], player: int = 1) -> vtk.vtkTextActor:
    """
    Create a futuristic neon text actor for displaying a score.

    Args:
        position: The screen position (x, y) for the text actor.
        player: Player number (1 or 2) for color coding.

    Returns:
        A VTK text actor configured for neon score display.
    """
    text_actor = vtk.vtkTextActor()
    text_actor.SetPosition(*position)
    text_property = text_actor.GetTextProperty()
    text_property.SetFontSize(48)  # Larger, more prominent
    text_property.BoldOn()
    
    # Neon color based on player
    if player == 1:
        text_property.SetColor(0.0, 1.0, 1.0)  # Neon cyan for player 1
    else:
        text_property.SetColor(0.0, 1.0, 0.4)  # Neon green for player 2
    
    # Add glow effect via shadow
    text_property.SetShadow(1)
    text_property.SetShadowOffset(2, -2)
    
    text_actor.SetInput("0")

    return text_actor
