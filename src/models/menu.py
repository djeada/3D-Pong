"""Main menu module for the 3D Pong game."""

from typing import Callable, List, Optional

import vtk


class MainMenu:
    """
    Main menu class for the 3D Pong game.

    Provides a simple menu interface for game mode selection.
    """

    MENU_SINGLE_PLAYER = 0
    MENU_TWO_PLAYER = 1

    def __init__(self, renderer: vtk.vtkRenderer, window_config: dict) -> None:
        """
        Initialize the main menu.

        Args:
            renderer: The VTK renderer.
            window_config: Window configuration containing width and height.
        """
        self.renderer = renderer
        self.window_width = window_config.get("width", 800)
        self.window_height = window_config.get("height", 600)
        self.selected_option = 0
        self.menu_options = ["Single Player (vs AI)", "Two Player"]
        self.visible = True
        self.on_selection: Optional[Callable[[int], None]] = None

        # Menu actors
        self.title_actor: Optional[vtk.vtkTextActor] = None
        self.option_actors: List[vtk.vtkTextActor] = []
        self.instruction_actor: Optional[vtk.vtkTextActor] = None

        self._create_menu_actors()

    def _create_menu_actors(self) -> None:
        """Create all menu text actors."""
        # Title
        self.title_actor = vtk.vtkTextActor()
        self.title_actor.SetInput("3D PONG")
        # Position title centered at top - use relative positioning
        self._position_title()
        title_prop = self.title_actor.GetTextProperty()
        title_prop.SetFontSize(64)
        title_prop.BoldOn()
        title_prop.SetColor(0.0, 1.0, 1.0)  # Neon cyan
        title_prop.SetShadow(1)
        title_prop.SetShadowOffset(3, -3)
        self.renderer.AddActor(self.title_actor)

        # Menu options
        for i, option in enumerate(self.menu_options):
            actor = vtk.vtkTextActor()
            actor.SetInput(option)
            prop = actor.GetTextProperty()
            prop.SetFontSize(32)
            prop.BoldOn()
            prop.SetShadow(1)
            prop.SetShadowOffset(2, -2)
            self.option_actors.append(actor)
            self.renderer.AddActor(actor)
        
        self._position_options()

        # Instructions
        self.instruction_actor = vtk.vtkTextActor()
        self.instruction_actor.SetInput("Use UP/DOWN arrows to select, ENTER to start")
        self._position_instructions()
        instr_prop = self.instruction_actor.GetTextProperty()
        instr_prop.SetFontSize(18)
        instr_prop.SetColor(0.6, 0.6, 0.6)
        instr_prop.SetOpacity(0.8)
        self.renderer.AddActor(self.instruction_actor)

        self._update_selection_colors()

    def _position_title(self) -> None:
        """Position title actor relative to window size."""
        # Centered horizontally, near top (85% of height)
        # Use percentage-based offset for responsiveness
        title_x = int(self.window_width * 0.5) - int(self.window_width * 0.05)
        title_y = int(self.window_height * 0.85)
        self.title_actor.SetPosition(title_x, title_y)

    def _position_options(self) -> None:
        """Position option actors relative to window size."""
        # Center vertically and horizontally with percentage-based offsets
        base_y = int(self.window_height * 0.55)
        center_x = int(self.window_width * 0.5) - int(self.window_width * 0.08)
        spacing = int(self.window_height * 0.1)
        for i, actor in enumerate(self.option_actors):
            actor.SetPosition(center_x, base_y - i * spacing)

    def _position_instructions(self) -> None:
        """Position instruction actor relative to window size."""
        # Centered horizontally, near bottom (15% of height)
        # Use percentage-based offset for responsiveness
        instr_x = int(self.window_width * 0.5) - int(self.window_width * 0.15)
        instr_y = int(self.window_height * 0.15)
        self.instruction_actor.SetPosition(instr_x, instr_y)

    def update_positions(self, window_width: int, window_height: int) -> None:
        """
        Update all menu element positions based on new window size.

        Args:
            window_width: New window width.
            window_height: New window height.
        """
        self.window_width = window_width
        self.window_height = window_height
        
        if self.title_actor:
            self._position_title()
        
        if self.option_actors:
            self._position_options()
        
        if self.instruction_actor:
            self._position_instructions()

    def _update_selection_colors(self) -> None:
        """Update option colors based on current selection."""
        for i, actor in enumerate(self.option_actors):
            prop = actor.GetTextProperty()
            if i == self.selected_option:
                prop.SetColor(1.0, 0.0, 0.5)  # Neon pink for selected
                actor.SetInput(f"> {self.menu_options[i]} <")
            else:
                prop.SetColor(0.5, 0.5, 0.5)  # Gray for unselected
                actor.SetInput(f"  {self.menu_options[i]}  ")

    def handle_key(self, key: str) -> bool:
        """
        Handle key press in menu.

        Args:
            key: The key pressed.

        Returns:
            True if menu should close, False otherwise.
        """
        if not self.visible or not key:
            return False

        if key == "Up":
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            self._update_selection_colors()
        elif key == "Down":
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            self._update_selection_colors()
        elif key == "Return":
            self.hide()
            if self.on_selection:
                self.on_selection(self.selected_option)
            return True

        return False

    def show(self) -> None:
        """Show the menu."""
        self.visible = True
        if self.title_actor:
            self.title_actor.SetVisibility(True)
        for actor in self.option_actors:
            actor.SetVisibility(True)
        if self.instruction_actor:
            self.instruction_actor.SetVisibility(True)

    def hide(self) -> None:
        """Hide the menu."""
        self.visible = False
        if self.title_actor:
            self.title_actor.SetVisibility(False)
        for actor in self.option_actors:
            actor.SetVisibility(False)
        if self.instruction_actor:
            self.instruction_actor.SetVisibility(False)

    def is_visible(self) -> bool:
        """Check if menu is visible."""
        return self.visible

    def get_selected_option(self) -> int:
        """Get the currently selected option index."""
        return self.selected_option
