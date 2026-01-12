"""Interactor module for handling game input and timer events."""

import logging
from typing import Any, Dict

import vtk

from src.interactors.ai_controller import AIController
from src.interactors.ball_controller import BallController
from src.interactors.paddle_controller import PaddleController
from src.interactors.score_manager import ScoreManager
from src.interactors.visual_effects import VisualEffects
from src.models.menu import MainMenu

logger = logging.getLogger(__name__)


class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    Custom interactor style for handling keyboard input and game logic.

    This class manages the game state, including pause/resume functionality,
    game reset, AI opponent, visual effects, and input handling.

    Features:
    - Single player mode with AI opponent (toggle with 'A' key)
    - Three difficulty levels (cycle with 'D' key)
    - Pause/Resume (Space key)
    - Reset game (R key)
    - Ball trail effect (T key to toggle)
    - Visual feedback for collisions and scoring
    """

    def __init__(
        self,
        actor: vtk.vtkActor,
        renderer: vtk.vtkRenderer,
        paddle1: vtk.vtkActor,
        paddle2: vtk.vtkActor,
        score1: vtk.vtkTextActor,
        score2: vtk.vtkTextActor,
        game_config: Dict[str, Any],
        render_window: vtk.vtkRenderWindow = None,
    ) -> None:
        """
        Initialize the interactor style.

        Args:
            actor: The ball actor.
            renderer: The VTK renderer.
            paddle1: The left paddle actor.
            paddle2: The right paddle actor.
            score1: The score text actor for player 1.
            score2: The score text actor for player 2.
            game_config: The game configuration dictionary.
            render_window: The VTK render window for responsive sizing.
        """
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.game_config = game_config
        # Game starts paused to show main menu; unpauses after mode selection
        self.paused = True
        self.ball_actor = actor

        # Game mode
        self.ai_enabled = False
        self.current_difficulty = AIController.DIFFICULTY_MEDIUM
        self.difficulty_cycle = [
            AIController.DIFFICULTY_EASY,
            AIController.DIFFICULTY_MEDIUM,
            AIController.DIFFICULTY_HARD,
        ]

        # Controllers
        self.paddle_controller = PaddleController(
            paddle1, paddle2, game_config.get("paddle")
        )

        # Score manager with win condition
        win_score = game_config.get("game", {}).get("win_score", 11)
        self.score_manager = ScoreManager(score1, score2, win_score)
        self.score_manager.on_game_over = self._on_game_over

        # Ball controller with callbacks
        self.ball_controller = BallController(
            actor, paddle1, paddle2, self.score_manager, game_config
        )
        self.ball_controller.on_paddle_hit = self._on_paddle_hit
        self.ball_controller.on_score = self._on_score

        # AI controller (for player 2 paddle)
        self.ai_controller = AIController(
            paddle2, actor, self.current_difficulty, game_config.get("paddle")
        )

        # Visual effects - Futuristic theme
        self.visual_effects = VisualEffects(renderer)
        self.visual_effects.set_dark_theme()
        self.visual_effects.reset_colors(actor, paddle1, paddle2)
        self.visual_effects.create_arena_grid()

        # Main menu
        self.main_menu = MainMenu(renderer, game_config.get("window", {}))
        self.main_menu.on_selection = self._on_menu_selection

        # Status text actor
        self.status_actor = self._create_status_actor()
        renderer.AddActor(self.status_actor)
        self.status_actor.SetVisibility(False)  # Hide until game starts

        # Game over text actor
        self.game_over_actor = self._create_game_over_actor()
        renderer.AddActor(self.game_over_actor)
        self.game_over_actor.SetVisibility(False)

        # Hide game elements until menu selection
        self._hide_game_elements()

        self.timer_id = None
        self.AddObserver("KeyPressEvent", self.key_press_event)
        logger.info("KeyPressInteractorStyle initialized with new features.")

    def _get_window_size(self) -> tuple:
        """Get current window size from render window or config."""
        if self.render_window:
            return self.render_window.GetSize()
        return (
            self.game_config.get("window", {}).get("width", 800),
            self.game_config.get("window", {}).get("height", 600),
        )

    def _create_status_actor(self) -> vtk.vtkTextActor:
        """Create futuristic neon status text actor for displaying game info."""
        actor = vtk.vtkTextActor()
        # Position at bottom left with small margin
        actor.SetPosition(10, 10)
        prop = actor.GetTextProperty()
        prop.SetFontSize(14)
        prop.SetColor(0.0, 0.8, 1.0)  # Neon cyan
        prop.SetOpacity(0.8)
        prop.BoldOn()
        self._update_status_text()
        return actor

    def _create_game_over_actor(self) -> vtk.vtkTextActor:
        """Create futuristic neon game over text actor."""
        actor = vtk.vtkTextActor()
        # Position at center of window
        window_width, window_height = self._get_window_size()
        actor.SetPosition(int(window_width * 0.5), int(window_height * 0.5))
        prop = actor.GetTextProperty()
        prop.SetFontSize(42)
        prop.BoldOn()
        prop.SetColor(1.0, 0.0, 0.5)  # Neon pink
        prop.SetJustificationToCentered()
        prop.SetVerticalJustificationToCentered()
        prop.SetShadow(1)
        prop.SetShadowOffset(2, -2)
        return actor

    def _update_status_text(self) -> None:
        """Update the status text with current game mode."""
        mode = "AI" if self.ai_enabled else "2P"
        difficulty = self.current_difficulty.upper() if self.ai_enabled else ""
        status = f"◆ MODE: {mode} {difficulty} | [A]I [D]ifficulty [R]eset [SPACE]Pause [T]rail ◆"
        if hasattr(self, "status_actor"):
            self.status_actor.SetInput(status)

    def update_label_positions(self) -> None:
        """Update all label positions based on current window size."""
        window_width, window_height = self._get_window_size()

        # Update score positions
        score1_x = int(window_width * 0.25)
        score2_x = int(window_width * 0.75)
        score_y = int(window_height * 0.9)
        self.score_manager.score1.SetPosition(score1_x, score_y)
        self.score_manager.score2.SetPosition(score2_x, score_y)

        # Update game over actor position (centered)
        self.game_over_actor.SetPosition(
            int(window_width * 0.5), int(window_height * 0.5)
        )

        # Update menu positions
        self.main_menu.update_positions(window_width, window_height)

    def _on_paddle_hit(self, paddle: vtk.vtkActor) -> None:
        """Callback when ball hits a paddle."""
        self.visual_effects.paddle_hit_effect(paddle, self.ball_actor)
        # Update ball color based on speed
        speed = self.ball_controller.get_speed()
        self.visual_effects.apply_speed_color(self.ball_actor, speed)

    def _on_score(self, player: int) -> None:
        """Callback when a player scores."""
        self.visual_effects.flash_score(player)

    def _on_game_over(self, winner: int) -> None:
        """Callback when game ends."""
        self.paused = True
        player_name = (
            "Player 1" if winner == 1 else ("AI" if self.ai_enabled else "Player 2")
        )
        self.game_over_actor.SetInput(f"{player_name} WINS!\nPress R to restart")
        self.game_over_actor.SetVisibility(True)
        logger.info(f"Game over! {player_name} wins!")

    def _on_menu_selection(self, option: int) -> None:
        """Handle menu selection callback."""
        if option == MainMenu.MENU_SINGLE_PLAYER:
            self.ai_enabled = True
            logger.info("Single player mode selected (vs AI)")
        else:
            self.ai_enabled = False
            logger.info("Two player mode selected")

        self._show_game_elements()
        self._update_status_text()
        self.paused = False

    def _hide_game_elements(self) -> None:
        """Hide game elements while menu is visible."""
        self.ball_actor.SetVisibility(False)
        self.paddle_controller.paddle1.SetVisibility(False)
        self.paddle_controller.paddle2.SetVisibility(False)
        self.score_manager.score1.SetVisibility(False)
        self.score_manager.score2.SetVisibility(False)

    def _show_game_elements(self) -> None:
        """Show game elements when game starts."""
        self.ball_actor.SetVisibility(True)
        self.paddle_controller.paddle1.SetVisibility(True)
        self.paddle_controller.paddle2.SetVisibility(True)
        self.score_manager.score1.SetVisibility(True)
        self.score_manager.score2.SetVisibility(True)
        self.status_actor.SetVisibility(True)

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.ball_controller.reset()
        self.paddle_controller.reset_positions()
        self.score_manager.reset()
        self.visual_effects.clear_trail()
        self.visual_effects.reset_colors(
            self.ball_actor,
            self.paddle_controller.paddle1,
            self.paddle_controller.paddle2,
        )
        self.game_over_actor.SetVisibility(False)
        self.paused = False
        logger.info("Game reset. Ball position, paddles, and scores reset.")

    def toggle_pause(self) -> None:
        """Toggle the game pause state."""
        if self.score_manager.game_over:
            return
        self.paused = not self.paused
        state = "paused" if self.paused else "resumed"
        logger.info(f"Game {state}.")

    def toggle_ai(self) -> None:
        """Toggle AI opponent mode."""
        self.ai_enabled = not self.ai_enabled
        mode = "AI" if self.ai_enabled else "Two-player"
        logger.info(f"Game mode changed to: {mode}")
        self._update_status_text()

    def cycle_difficulty(self) -> None:
        """Cycle through difficulty levels."""
        idx = self.difficulty_cycle.index(self.current_difficulty)
        idx = (idx + 1) % len(self.difficulty_cycle)
        self.current_difficulty = self.difficulty_cycle[idx]
        self.ai_controller.set_difficulty(self.current_difficulty)
        logger.info(f"Difficulty changed to: {self.current_difficulty}")
        self._update_status_text()

    def key_press_event(self, obj: vtk.vtkObject, event: str) -> None:
        """
        Handle key press events.

        Args:
            obj: The VTK object that triggered the event.
            event: The event type string.
        """
        key = self.GetInteractor().GetKeySym()

        # Guard against None or empty key values
        if not key:
            return

        logger.debug(f"Key pressed: {key}")

        # Handle menu input first if menu is visible
        if self.main_menu.is_visible():
            self.main_menu.handle_key(key)
            return

        if key == "space":
            self.toggle_pause()
        elif key == "r" or key == "R":
            self.reset()
        elif key == "a" or key == "A":
            self.toggle_ai()
        elif key == "d" or key == "D":
            self.cycle_difficulty()
        elif key == "t" or key == "T":
            self.visual_effects.toggle_trail()
        elif not self.paused and not self.score_manager.game_over:
            self.paddle_controller.move_paddles(key)

    def execute(self, obj: vtk.vtkObject, event: str) -> None:
        """
        Execute the game loop update with futuristic visual effects.

        Args:
            obj: The VTK object that triggered the event.
            event: The event type string.
        """
        if not self.paused and not self.score_manager.game_over:
            self.ball_controller.execute()

            # Update AI if enabled
            if self.ai_enabled:
                self.ai_controller.update(self.ball_controller.direction)

            # Update trail effect
            if self.visual_effects.trail_enabled:
                self.visual_effects.update_ball_trail(self.ball_actor)

            # Update pulsing glow effects
            self.visual_effects.update_pulsing_effects(
                self.ball_actor,
                self.paddle_controller.paddle1,
                self.paddle_controller.paddle2,
            )

        # Update visual effects (particles, flash, background animation)
        self.visual_effects.update_flash()
        self.visual_effects.update_particles()

        self.GetInteractor().GetRenderWindow().Render()
