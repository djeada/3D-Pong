"""Game module containing the main Game class."""

from typing import Any, Dict, Tuple

import vtk

from src.config.config import load_config
from src.custom_actors.ball import create_ball
from src.custom_actors.border import create_border
from src.custom_actors.paddle import create_paddle
from src.custom_actors.score import create_text_actor
from src.interactors.interactor import KeyPressInteractorStyle


class Game:
    """
    Main game class for the 3D Pong game.

    Manages the game window, renderer, and all game actors including
    the ball, paddles, scores, and borders.
    """

    def __init__(self, config_file: str) -> None:
        """
        Initialize the game with configuration.

        Args:
            config_file: Path to the YAML configuration file.
        """
        self.config: Dict[str, Any] = load_config(config_file)
        self.renderer: vtk.vtkRenderer = vtk.vtkRenderer()
        self.render_window: vtk.vtkRenderWindow = vtk.vtkRenderWindow()
        self.interactor: vtk.vtkRenderWindowInteractor = vtk.vtkRenderWindowInteractor()
        self.style: KeyPressInteractorStyle | None = None

        self.ball_actor: vtk.vtkActor | None = None
        self.paddle1: vtk.vtkActor | None = None
        self.paddle2: vtk.vtkActor | None = None
        self.score1: vtk.vtkTextActor | None = None
        self.score2: vtk.vtkTextActor | None = None

    def initialize(self) -> None:
        """Initialize all game components and set up the window."""
        self.setup_renderer()
        self.setup_render_window()
        self.setup_camera()
        self.create_actors()
        self.setup_interactor()
        self.setup_resize_callback()

    def create_actors(self) -> None:
        """Create all game actors (ball, paddles, scores, borders) with futuristic styling."""
        self.ball_actor = create_ball(self.config["ball"])
        self.paddle1 = create_paddle(self.config["paddle"])
        self.paddle1.SetPosition(-0.9, 0, 0)
        self.paddle2 = create_paddle(self.config["paddle"])
        self.paddle2.SetPosition(0.9, 0, 0)

        # Get current window size for responsive positioning
        window_size = self.render_window.GetSize()
        window_width = window_size[0]
        window_height = window_size[1]

        # Scores with neon styling for each player - positioned relative to window size
        score1_x = int(window_width * 0.25)
        score2_x = int(window_width * 0.75)
        score_y = int(window_height * 0.9)
        self.score1 = create_text_actor((score1_x, score_y), player=1)
        self.score2 = create_text_actor((score2_x, score_y), player=2)

        borders = [
            create_border((-1.0, -1.0, 0.0), (-1.0, 1.0, 0.0)),
            create_border((-1.0, 1.0, 0.0), (1.0, 1.0, 0.0)),
            create_border((1.0, 1.0, 0.0), (1.0, -1.0, 0.0)),
            create_border((1.0, -1.0, 0.0), (-1.0, -1.0, 0.0)),
        ]

        self.renderer.AddActor(self.ball_actor)
        self.renderer.AddActor(self.paddle1)
        self.renderer.AddActor(self.paddle2)
        self.renderer.AddActor(self.score1)
        self.renderer.AddActor(self.score2)
        for border in borders:
            self.renderer.AddActor(border)

    def setup_renderer(self) -> None:
        """Set up the renderer and add it to the render window."""
        self.render_window.AddRenderer(self.renderer)

    def setup_render_window(self) -> None:
        """Configure the render window to full screen."""
        self.render_window.SetFullScreen(True)
        # Render once to ensure window size is available
        self.render_window.Render()

    def setup_camera(self) -> None:
        """Configure a stable camera that keeps the arena in view."""
        camera = self.renderer.GetActiveCamera()
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition(0, 0, 3)
        camera.SetViewUp(0, 1, 0)
        camera.ParallelProjectionOn()
        self.update_camera_scale()

    def update_camera_scale(self) -> None:
        """Update camera scale to keep the board within the viewport."""
        window_width, window_height = self.render_window.GetSize()
        if window_height <= 0:
            return

        aspect_ratio = window_width / window_height
        board_half_size = 1.0
        margin = 1.05

        if aspect_ratio >= 1.0:
            parallel_scale = board_half_size * margin
        else:
            parallel_scale = (board_half_size / aspect_ratio) * margin

        camera = self.renderer.GetActiveCamera()
        camera.SetParallelScale(parallel_scale)

    def setup_interactor(self) -> None:
        """Set up the interactor with the custom keyboard handler."""
        self.interactor.SetRenderWindow(self.render_window)

        # Update config with actual window size for responsive positioning
        window_size = self.render_window.GetSize()
        self.config["window"]["width"] = window_size[0]
        self.config["window"]["height"] = window_size[1]

        self.style = KeyPressInteractorStyle(
            self.ball_actor,
            self.renderer,
            self.paddle1,
            self.paddle2,
            self.score1,
            self.score2,
            self.config,
            self.render_window,
        )
        self.interactor.SetInteractorStyle(self.style)
        self.interactor.Initialize()
        self.interactor.CreateRepeatingTimer(1)
        self.interactor.AddObserver("TimerEvent", self.style.execute)

    def setup_resize_callback(self) -> None:
        """Set up callback to handle window resize events."""
        # Store last known size to detect actual resize events
        self._last_window_size = self.render_window.GetSize()

        def on_window_modified(obj: vtk.vtkObject, event: str) -> None:
            """Handle window resize event to update label positions."""
            if self.style:
                current_size = self.render_window.GetSize()
                # Only update if window size actually changed
                if current_size != self._last_window_size:
                    self._last_window_size = current_size
                    self.update_camera_scale()
                    self.style.update_label_positions()

        self.render_window.AddObserver("ModifiedEvent", on_window_modified)

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """
        Get the screen size using VTK.

        Returns:
            A tuple of (width, height) representing the screen dimensions.
        """
        temp_window = vtk.vtkRenderWindow()
        temp_window.OffScreenRenderingOn()
        temp_window.Render()

        screen_size = temp_window.GetScreenSize()
        temp_window.Finalize()

        return screen_size

    def start(self) -> None:
        """Start the game loop."""
        self.interactor.Start()
