"""Visual effects module for game visual feedback."""

import logging
import math
import random
from typing import List, Tuple

import vtk

logger = logging.getLogger(__name__)


class VisualEffects:
    """
    Manager for visual effects in the game.

    Handles modern futuristic effects including neon glows, particles,
    animated backgrounds, and dynamic lighting.
    """

    # Futuristic neon color palette
    COLOR_WHITE = (1.0, 1.0, 1.0)
    COLOR_NEON_PINK = (1.0, 0.0, 0.5)
    COLOR_NEON_BLUE = (0.0, 0.8, 1.0)
    COLOR_NEON_PURPLE = (0.6, 0.0, 1.0)
    COLOR_NEON_GREEN = (0.0, 1.0, 0.4)
    COLOR_NEON_ORANGE = (1.0, 0.4, 0.0)
    COLOR_NEON_CYAN = (0.0, 1.0, 1.0)
    COLOR_NEON_YELLOW = (1.0, 1.0, 0.0)
    COLOR_ELECTRIC_BLUE = (0.1, 0.5, 1.0)

    # Legacy color aliases for compatibility
    COLOR_RED = COLOR_NEON_PINK
    COLOR_BLUE = COLOR_ELECTRIC_BLUE
    COLOR_GREEN = COLOR_NEON_GREEN
    COLOR_YELLOW = COLOR_NEON_YELLOW
    COLOR_ORANGE = COLOR_NEON_ORANGE
    COLOR_CYAN = COLOR_NEON_CYAN

    # Effect configuration constants
    MAX_TRAIL_LENGTH = 25
    MAX_PARTICLES = 50
    CELEBRATION_PARTICLE_COUNT = 20
    IMPACT_PARTICLE_COUNT = 12
    CELEBRATION_SPAWN_RANGE = 0.5  # Y-axis range for particle spawn

    # Pulse effect constants
    PULSE_BASE = 0.3
    PULSE_AMPLITUDE = 0.1
    BALL_PULSE_BASE = 0.4
    BALL_PULSE_AMPLITUDE = 0.2
    PULSE_SPEED = 0.1

    # Grid configuration
    GRID_POSITIONS = [-0.8, -0.4, 0, 0.4, 0.8]
    GRID_OPACITY = 0.15
    CENTER_LINE_OPACITY = 0.4

    def __init__(self, renderer: vtk.vtkRenderer) -> None:
        """
        Initialize the visual effects manager.

        Args:
            renderer: The VTK renderer for adding effects.
        """
        self.renderer = renderer
        self.flash_duration = 0
        self.flash_actor: vtk.vtkActor | None = None
        self.trail_actors: List[vtk.vtkActor] = []
        self.max_trail_length = self.MAX_TRAIL_LENGTH
        self.trail_enabled = True

        # Store original colors
        self.original_colors: dict = {}

        # Particle system for collision effects
        self.particle_actors: List[vtk.vtkActor] = []
        self.particle_velocities: List[List[float]] = []
        self.max_particles = self.MAX_PARTICLES

        # Glow actors for neon effect
        self.glow_actors: List[vtk.vtkActor] = []

        # Animation state
        self.animation_frame = 0
        self.pulse_phase = 0.0

        # Grid lines for arena
        self.grid_actors: List[vtk.vtkActor] = []

        # Score celebration particles
        self.celebration_particles: List[vtk.vtkActor] = []
        self.celebration_velocities: List[List[float]] = []

        # Background gradient animation
        self.bg_phase = 0.0

        logger.info("Visual effects manager initialized with futuristic effects.")

    def flash_score(self, player: int) -> None:
        """
        Create a dramatic neon flash effect when a player scores.

        Args:
            player: Player number (1 or 2) who scored.
        """
        color = self.COLOR_NEON_BLUE if player == 1 else self.COLOR_NEON_PINK
        self.flash_duration = 20  # Longer flash for dramatic effect
        self.renderer.SetBackground(*[c * 0.3 for c in color])

        # Spawn celebration particles
        self._spawn_celebration_particles(player)
        logger.debug(f"Neon score flash triggered for player {player}")

    def _spawn_celebration_particles(self, player: int) -> None:
        """Spawn celebration particle burst when scoring."""
        # Determine spawn position based on which side scored
        spawn_x = -0.9 if player == 2 else 0.9

        for _ in range(self.CELEBRATION_PARTICLE_COUNT):
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(0.01)
            sphere.SetPhiResolution(6)
            sphere.SetThetaResolution(6)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())

            particle = vtk.vtkActor()
            particle.SetMapper(mapper)
            spawn_range = self.CELEBRATION_SPAWN_RANGE
            particle.SetPosition(spawn_x, random.uniform(-spawn_range, spawn_range), 0)

            # Random neon color for each particle
            colors = [
                self.COLOR_NEON_PINK,
                self.COLOR_NEON_BLUE,
                self.COLOR_NEON_PURPLE,
                self.COLOR_NEON_CYAN,
            ]
            particle.GetProperty().SetColor(*random.choice(colors))
            particle.GetProperty().SetOpacity(1.0)

            self.celebration_particles.append(particle)
            self.celebration_velocities.append(
                [random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), 0]
            )
            self.renderer.AddActor(particle)

    def update_flash(self) -> None:
        """Update flash effect countdown and animate background."""
        if self.flash_duration > 0:
            self.flash_duration -= 1
            # Smooth fade out
            fade = self.flash_duration / 20.0
            self.renderer.SetBackground(
                0.02 + 0.08 * fade, 0.02 + 0.05 * fade, 0.05 + 0.1 * fade
            )
            if self.flash_duration == 0:
                self._set_animated_background()

        # Update celebration particles
        self._update_celebration_particles()

        # Update ambient background animation
        self._update_ambient_animation()

    def _update_celebration_particles(self) -> None:
        """Update and remove celebration particles."""
        particles_to_remove = []
        for i, particle in enumerate(self.celebration_particles):
            pos = list(particle.GetPosition())
            vel = self.celebration_velocities[i]

            # Apply velocity and gravity
            pos[0] += vel[0]
            pos[1] += vel[1]
            vel[1] -= 0.002  # Gravity

            particle.SetPosition(*pos)

            # Fade out
            opacity = particle.GetProperty().GetOpacity()
            particle.GetProperty().SetOpacity(opacity * 0.95)

            # Remove if faded or out of bounds
            if opacity < 0.05 or abs(pos[0]) > 1.5 or abs(pos[1]) > 1.5:
                particles_to_remove.append(i)

        # Remove dead particles
        for i in reversed(particles_to_remove):
            self.renderer.RemoveActor(self.celebration_particles[i])
            self.celebration_particles.pop(i)
            self.celebration_velocities.pop(i)

    def _update_ambient_animation(self) -> None:
        """Update subtle ambient background animation."""
        self.bg_phase += 0.01
        if self.flash_duration == 0:
            # Subtle color shift for ambient effect
            r = 0.02 + 0.01 * math.sin(self.bg_phase)
            g = 0.02 + 0.01 * math.sin(self.bg_phase + 2)
            b = 0.05 + 0.02 * math.sin(self.bg_phase + 4)
            self.renderer.SetBackground(r, g, b)

    def _set_animated_background(self) -> None:
        """Set the base animated background color."""
        self.renderer.SetBackground(0.02, 0.02, 0.05)

    def set_ball_color(
        self, ball: vtk.vtkActor, color: Tuple[float, float, float]
    ) -> None:
        """
        Set the ball color.

        Args:
            ball: The ball actor.
            color: RGB color tuple (0.0-1.0 for each component).
        """
        ball.GetProperty().SetColor(*color)

    def set_paddle_color(
        self, paddle: vtk.vtkActor, color: Tuple[float, float, float]
    ) -> None:
        """
        Set a paddle color.

        Args:
            paddle: The paddle actor.
            color: RGB color tuple.
        """
        paddle.GetProperty().SetColor(*color)

    def paddle_hit_effect(self, paddle: vtk.vtkActor, ball: vtk.vtkActor) -> None:
        """
        Apply spectacular neon visual effect when paddle hits ball.

        Args:
            paddle: The paddle that hit the ball.
            ball: The ball actor.
        """
        # Neon flash on paddle
        self.set_paddle_color(paddle, self.COLOR_NEON_YELLOW)
        self.set_ball_color(ball, self.COLOR_NEON_ORANGE)

        # Spawn impact particles
        self._spawn_impact_particles(ball.GetPosition())

    def _spawn_impact_particles(self, position: tuple) -> None:
        """Spawn particle burst at impact location."""
        for _ in range(self.IMPACT_PARTICLE_COUNT):
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(0.008)
            sphere.SetPhiResolution(4)
            sphere.SetThetaResolution(4)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())

            particle = vtk.vtkActor()
            particle.SetMapper(mapper)
            particle.SetPosition(position[0], position[1], 0)

            # Random neon color
            colors = [
                self.COLOR_NEON_CYAN,
                self.COLOR_NEON_YELLOW,
                self.COLOR_NEON_ORANGE,
                self.COLOR_WHITE,
            ]
            particle.GetProperty().SetColor(*random.choice(colors))
            particle.GetProperty().SetOpacity(0.9)

            self.particle_actors.append(particle)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.02, 0.05)
            self.particle_velocities.append(
                [speed * math.cos(angle), speed * math.sin(angle), 0]
            )
            self.renderer.AddActor(particle)

    def update_particles(self) -> None:
        """Update and remove impact particles."""
        particles_to_remove = []
        for i, particle in enumerate(self.particle_actors):
            pos = list(particle.GetPosition())
            vel = self.particle_velocities[i]

            pos[0] += vel[0]
            pos[1] += vel[1]

            particle.SetPosition(*pos)

            # Fade out
            opacity = particle.GetProperty().GetOpacity()
            particle.GetProperty().SetOpacity(opacity * 0.9)

            if opacity < 0.05:
                particles_to_remove.append(i)

        for i in reversed(particles_to_remove):
            self.renderer.RemoveActor(self.particle_actors[i])
            self.particle_actors.pop(i)
            self.particle_velocities.pop(i)

    def reset_colors(
        self, ball: vtk.vtkActor, paddle1: vtk.vtkActor, paddle2: vtk.vtkActor
    ) -> None:
        """
        Reset all game object colors to futuristic neon defaults.

        Args:
            ball: The ball actor.
            paddle1: First paddle actor.
            paddle2: Second paddle actor.
        """
        self.set_ball_color(ball, self.COLOR_WHITE)
        self.set_paddle_color(paddle1, self.COLOR_NEON_CYAN)
        self.set_paddle_color(paddle2, self.COLOR_NEON_GREEN)

        # Apply neon glow effect to actors
        self._apply_neon_properties(ball)
        self._apply_neon_properties(paddle1)
        self._apply_neon_properties(paddle2)

    def _apply_neon_properties(self, actor: vtk.vtkActor) -> None:
        """Apply neon-like material properties to an actor."""
        prop = actor.GetProperty()
        prop.SetAmbient(0.4)  # Higher ambient for glow effect
        prop.SetDiffuse(0.6)
        prop.SetSpecular(1.0)
        prop.SetSpecularPower(100)
        prop.SetInterpolationToPhong()

    def update_ball_trail(self, ball: vtk.vtkActor) -> None:
        """
        Update the futuristic neon ball trail effect with rainbow gradient.

        Args:
            ball: The ball actor to trail.
        """
        if not self.trail_enabled:
            return

        ball_pos = ball.GetPosition()
        self.animation_frame += 1

        # Create trail sphere
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(0.018)  # Slightly smaller than ball
        sphere.SetPhiResolution(10)
        sphere.SetThetaResolution(10)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        trail_actor = vtk.vtkActor()
        trail_actor.SetMapper(mapper)
        trail_actor.SetPosition(ball_pos[0], ball_pos[1], ball_pos[2])

        # Rainbow neon gradient color based on animation frame
        hue = (self.animation_frame * 0.02) % 1.0
        color = self._hsv_to_rgb(hue, 1.0, 1.0)
        trail_actor.GetProperty().SetColor(*color)
        trail_actor.GetProperty().SetOpacity(0.8)

        # Apply neon material properties
        trail_actor.GetProperty().SetAmbient(0.5)
        trail_actor.GetProperty().SetDiffuse(0.5)

        self.trail_actors.append(trail_actor)
        self.renderer.AddActor(trail_actor)

        # Remove old trail segments
        while len(self.trail_actors) > self.max_trail_length:
            old_actor = self.trail_actors.pop(0)
            self.renderer.RemoveActor(old_actor)

        # Update opacity and size gradient of existing trail
        for i, actor in enumerate(self.trail_actors):
            progress = (i + 1) / len(self.trail_actors)
            actor.GetProperty().SetOpacity(progress * 0.7)
            # Rainbow color shift for trail
            trail_hue = (hue - (len(self.trail_actors) - i) * 0.03) % 1.0
            actor.GetProperty().SetColor(*self._hsv_to_rgb(trail_hue, 1.0, 1.0))

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB color values."""
        if s == 0.0:
            return (v, v, v)

        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6

        if i == 0:
            return (v, t, p)
        if i == 1:
            return (q, v, p)
        if i == 2:
            return (p, v, t)
        if i == 3:
            return (p, q, v)
        if i == 4:
            return (t, p, v)
        return (v, p, q)

    def clear_trail(self) -> None:
        """Clear all trail actors and particles."""
        for actor in self.trail_actors:
            self.renderer.RemoveActor(actor)
        self.trail_actors.clear()

        # Also clear any lingering particles
        for actor in self.particle_actors:
            self.renderer.RemoveActor(actor)
        self.particle_actors.clear()
        self.particle_velocities.clear()

        for actor in self.celebration_particles:
            self.renderer.RemoveActor(actor)
        self.celebration_particles.clear()
        self.celebration_velocities.clear()

    def toggle_trail(self) -> bool:
        """
        Toggle trail effect on/off.

        Returns:
            Current trail enabled state.
        """
        self.trail_enabled = not self.trail_enabled
        if not self.trail_enabled:
            self.clear_trail()
        logger.info(
            f"Neon trail effect {'enabled' if self.trail_enabled else 'disabled'}"
        )
        return self.trail_enabled

    def set_dark_theme(self) -> None:
        """Apply futuristic dark cyber theme to the renderer."""
        self.renderer.SetBackground(0.02, 0.02, 0.05)  # Deep space blue-black
        self._setup_futuristic_lighting()
        logger.debug("Futuristic cyber theme applied")

    def _setup_futuristic_lighting(self) -> None:
        """Setup dramatic lighting for futuristic effect."""
        # Remove existing lights
        self.renderer.RemoveAllLights()

        # Main light - cool blue tint
        main_light = vtk.vtkLight()
        main_light.SetColor(0.8, 0.9, 1.0)
        main_light.SetPosition(0, 1, 2)
        main_light.SetFocalPoint(0, 0, 0)
        main_light.SetIntensity(0.8)
        self.renderer.AddLight(main_light)

        # Accent light - purple/pink tint from left
        accent1 = vtk.vtkLight()
        accent1.SetColor(0.8, 0.4, 1.0)
        accent1.SetPosition(-2, 0, 1)
        accent1.SetFocalPoint(0, 0, 0)
        accent1.SetIntensity(0.3)
        self.renderer.AddLight(accent1)

        # Accent light - cyan tint from right
        accent2 = vtk.vtkLight()
        accent2.SetColor(0.4, 1.0, 1.0)
        accent2.SetPosition(2, 0, 1)
        accent2.SetFocalPoint(0, 0, 0)
        accent2.SetIntensity(0.3)
        self.renderer.AddLight(accent2)

    def apply_speed_color(self, ball: vtk.vtkActor, speed: float) -> None:
        """
        Change ball color based on speed with neon gradient.

        Args:
            ball: The ball actor.
            speed: Current ball speed magnitude.
        """
        # Neon gradient from cyan to pink based on speed
        normalized_speed = min(speed / 0.05, 1.0)  # Normalize to 0-1

        # Interpolate from cyan (slow) to hot pink (fast)
        r = 0.0 + normalized_speed * 1.0
        g = 1.0 - normalized_speed * 0.8
        b = 1.0 - normalized_speed * 0.2
        self.set_ball_color(ball, (r, g, b))

    def create_arena_grid(self) -> None:
        """Create futuristic grid lines for the arena floor."""
        # Horizontal grid lines
        for y in self.GRID_POSITIONS:
            line = vtk.vtkLineSource()
            line.SetPoint1(-1.0, y, -0.01)
            line.SetPoint2(1.0, y, -0.01)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(line.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(*self.COLOR_NEON_PURPLE)
            actor.GetProperty().SetOpacity(self.GRID_OPACITY)
            actor.GetProperty().SetLineWidth(1)

            self.grid_actors.append(actor)
            self.renderer.AddActor(actor)

        # Vertical grid lines
        for x in self.GRID_POSITIONS:
            line = vtk.vtkLineSource()
            line.SetPoint1(x, -1.0, -0.01)
            line.SetPoint2(x, 1.0, -0.01)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(line.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(*self.COLOR_NEON_PURPLE)
            actor.GetProperty().SetOpacity(self.GRID_OPACITY)
            actor.GetProperty().SetLineWidth(1)

            self.grid_actors.append(actor)
            self.renderer.AddActor(actor)

        # Center line - brighter
        center_line = vtk.vtkLineSource()
        center_line.SetPoint1(0, -1.0, -0.005)
        center_line.SetPoint2(0, 1.0, -0.005)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(center_line.GetOutputPort())

        center_actor = vtk.vtkActor()
        center_actor.SetMapper(mapper)
        center_actor.GetProperty().SetColor(*self.COLOR_NEON_CYAN)
        center_actor.GetProperty().SetOpacity(self.CENTER_LINE_OPACITY)
        center_actor.GetProperty().SetLineWidth(2)

        self.grid_actors.append(center_actor)
        self.renderer.AddActor(center_actor)

        logger.debug("Futuristic arena grid created")

    def update_pulsing_effects(
        self, ball: vtk.vtkActor, paddle1: vtk.vtkActor, paddle2: vtk.vtkActor
    ) -> None:
        """Apply subtle pulsing glow effect to game elements."""
        self.pulse_phase += self.PULSE_SPEED
        pulse = self.PULSE_BASE + self.PULSE_AMPLITUDE * math.sin(self.pulse_phase)

        # Apply pulsing ambient to paddles
        paddle1.GetProperty().SetAmbient(pulse)
        paddle2.GetProperty().SetAmbient(pulse)

        # Ball has faster pulse
        ball_pulse = self.BALL_PULSE_BASE + self.BALL_PULSE_AMPLITUDE * math.sin(
            self.pulse_phase * 2
        )
        ball.GetProperty().SetAmbient(ball_pulse)
