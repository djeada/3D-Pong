from typing import Any, Dict, Tuple

import vtk

from src.config.config import load_config
from src.custom_actors.ball import create_ball
from src.custom_actors.border import create_border
from src.custom_actors.paddle import create_paddle
from src.custom_actors.score import create_text_actor
from src.interactors.interactor import KeyPressInteractorStyle


class Game:
    def __init__(self, config_file: str) -> None:
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
        self.create_actors()
        self.setup_renderer()
        self.setup_render_window()
        self.setup_interactor()
        self.center_window()

    def create_actors(self) -> None:
        self.ball_actor = create_ball(self.config["ball"])
        self.paddle1 = create_paddle(self.config["paddle"])
        self.paddle1.SetPosition(-0.9, 0, 0)
        self.paddle2 = create_paddle(self.config["paddle"])
        self.paddle2.SetPosition(0.9, 0, 0)

        self.score1 = create_text_actor((200, 560))
        self.score2 = create_text_actor((600, 560))

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
        self.render_window.AddRenderer(self.renderer)

    def setup_render_window(self) -> None:
        self.render_window.SetSize(
            self.config["window"]["width"], self.config["window"]["height"]
        )

    def setup_interactor(self) -> None:
        self.interactor.SetRenderWindow(self.render_window)
        self.style = KeyPressInteractorStyle(
            self.ball_actor,
            self.renderer,
            self.paddle1,
            self.paddle2,
            self.score1,
            self.score2,
            self.config,
        )
        self.interactor.SetInteractorStyle(self.style)
        self.interactor.Initialize()
        self.interactor.CreateRepeatingTimer(1)
        self.interactor.AddObserver("TimerEvent", self.style.execute)

    def center_window(self) -> None:
        screen_width, screen_height = self.get_screen_size()
        window_width = self.config["window"]["width"]
        window_height = self.config["window"]["height"]
        self.render_window.SetPosition(
            (screen_width - window_width) // 2, (screen_height - window_height) // 2
        )

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        temp_window = vtk.vtkRenderWindow()
        temp_window.OffScreenRenderingOn()
        temp_window.Render()

        screen_size = temp_window.GetScreenSize()
        temp_window.Finalize()

        return screen_size

    def start(self) -> None:
        self.interactor.Start()
