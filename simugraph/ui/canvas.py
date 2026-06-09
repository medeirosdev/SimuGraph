"""
Canvas — draws the infinite grid and will host all graph rendering.

The grid lines are spaced every GRID_MINOR world-units, with a major line
every GRID_MAJOR_FACTOR minor lines. Camera offset and zoom are applied via
the Camera instance so the grid scrolls and scales correctly.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg
from simugraph.camera import Camera
from simugraph.core.graph import Graph

# World-space spacing between minor grid lines
GRID_MINOR: int = 50
# Every N-th minor line is drawn as a major (brighter) line
GRID_MAJOR_FACTOR: int = 5


class Canvas:
    """
    Responsible for drawing the background grid and (later) nodes/edges.

    Draws into a dedicated SRCALPHA surface that is blitted onto the main
    screen each frame.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw(self, camera: Camera, graph: Graph) -> None:
        """Clear the surface and redraw everything for one frame."""
        self.surface.fill((0, 0, 0, 0))
        self._draw_grid(camera)
        # Future commits will call self._draw_edges(camera, graph) etc.

    # ------------------------------------------------------------------
    # Grid
    # ------------------------------------------------------------------

    def _draw_grid(self, camera: Camera) -> None:
        """
        Draw minor and major grid lines whose spacing is constant in
        world-space but correctly scaled by the camera zoom.
        """
        grid_minor_color = cfg.THEME["grid"]
        grid_major_color = cfg.THEME["grid_major"]

        # Pixel distance between minor lines at current zoom
        step_px = GRID_MINOR * camera.zoom

        # World coordinate of the top-left screen corner
        world_x0, world_y0 = camera.screen_to_world(0, 0)

        # Index of the first visible minor line (left / top)
        import math
        first_col = math.floor(world_x0 / GRID_MINOR)
        first_row = math.floor(world_y0 / GRID_MINOR)

        # Vertical lines
        col = first_col
        while True:
            wx = col * GRID_MINOR
            sx, _ = camera.world_to_screen(wx, 0)
            if sx > self.width:
                break
            is_major = (col % GRID_MAJOR_FACTOR == 0)
            color = grid_major_color if is_major else grid_minor_color
            width = 2 if is_major else 1
            pygame.draw.line(self.surface, color, (sx, 0), (sx, self.height), width)
            col += 1

        # Horizontal lines
        row = first_row
        while True:
            wy = row * GRID_MINOR
            _, sy = camera.world_to_screen(0, wy)
            if sy > self.height:
                break
            is_major = (row % GRID_MAJOR_FACTOR == 0)
            color = grid_major_color if is_major else grid_minor_color
            width = 2 if is_major else 1
            pygame.draw.line(self.surface, color, (0, sy), (self.width, sy), width)
            row += 1

        # World-space origin cross-hair (always drawn)
        ox, oy = camera.world_to_screen(0, 0)
        if 0 <= ox <= self.width:
            pygame.draw.line(
                self.surface, (*cfg.THEME["accent"][:3], 60),
                (ox, 0), (ox, self.height), 1,
            )
        if 0 <= oy <= self.height:
            pygame.draw.line(
                self.surface, (*cfg.THEME["accent"][:3], 60),
                (0, oy), (self.width, oy), 1,
            )
