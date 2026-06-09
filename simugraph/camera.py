"""
Camera — handles world↔screen coordinate transforms, pan, and zoom.

World coordinates: the infinite logical canvas where nodes live.
Screen coordinates: the actual pixel positions on the pygame window.

Relationship:
    screen_x = (world_x - offset_x) * zoom
    screen_y = (world_y - offset_y) * zoom

    world_x  = screen_x / zoom + offset_x
    world_y  = screen_y / zoom + offset_y
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.node import Node


class Camera:
    """
    Manages the viewport into the infinite graph canvas.

    Attributes:
        offset_x / offset_y : top-left world coordinate visible at screen (0,0)
        zoom                : scale factor (1.0 = 100 %)
    """

    ZOOM_MIN: float = 0.1
    ZOOM_MAX: float = 5.0

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        zoom: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = zoom
        self.offset_x = offset_x
        self.offset_y = offset_y

    # ------------------------------------------------------------------
    # Core transforms
    # ------------------------------------------------------------------

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        """Convert world-space coordinates to screen-space pixels."""
        sx = (wx - self.offset_x) * self.zoom
        sy = (wy - self.offset_y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen-space pixels to world-space coordinates."""
        wx = sx / self.zoom + self.offset_x
        wy = sy / self.zoom + self.offset_y
        return wx, wy

    # ------------------------------------------------------------------
    # Pan
    # ------------------------------------------------------------------

    def pan(self, dx: float, dy: float) -> None:
        """
        Move the camera by (dx, dy) screen pixels.
        Translates to world offset so panning feels 1:1 with mouse movement.
        """
        self.offset_x -= dx / self.zoom
        self.offset_y -= dy / self.zoom

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------

    def zoom_at(self, sx: float, sy: float, factor: float) -> None:
        """
        Zoom in/out keeping the world point under (sx, sy) stationary.

        factor > 1.0 → zoom in
        factor < 1.0 → zoom out
        """
        wx, wy = self.screen_to_world(sx, sy)
        new_zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self.zoom * factor))
        self.offset_x = wx - sx / new_zoom
        self.offset_y = wy - sy / new_zoom
        self.zoom = new_zoom

    def reset_zoom(self) -> None:
        """Reset zoom to 100 % keeping the screen center fixed."""
        cx = self.screen_width / 2
        cy = self.screen_height / 2
        wx, wy = self.screen_to_world(cx, cy)
        self.zoom = 1.0
        self.offset_x = wx - cx / self.zoom
        self.offset_y = wy - cy / self.zoom

    # ------------------------------------------------------------------
    # Fit
    # ------------------------------------------------------------------

    def fit_to_nodes(self, nodes: list[Node], padding: int = 80) -> None:
        """
        Adjust offset and zoom so all nodes are visible with padding.
        No-op if the node list is empty.
        """
        if not nodes:
            return

        xs = [n.x for n in nodes]
        ys = [n.y for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        world_w = max_x - min_x or 1.0
        world_h = max_y - min_y or 1.0

        avail_w = self.screen_width - 2 * padding
        avail_h = self.screen_height - 2 * padding

        self.zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, min(avail_w / world_w, avail_h / world_h)))

        center_wx = (min_x + max_x) / 2
        center_wy = (min_y + max_y) / 2
        self.offset_x = center_wx - (self.screen_width / 2) / self.zoom
        self.offset_y = center_wy - (self.screen_height / 2) / self.zoom

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def zoom_percent(self) -> int:
        return round(self.zoom * 100)

    def is_visible(self, wx: float, wy: float, margin: float = 0.0) -> bool:
        """True if a world point is within the visible screen area (+margin px)."""
        sx, sy = self.world_to_screen(wx, wy)
        return (
            -margin <= sx <= self.screen_width + margin
            and -margin <= sy <= self.screen_height + margin
        )

    def __repr__(self) -> str:
        return (
            f"Camera(zoom={self.zoom:.2f}, "
            f"offset=({self.offset_x:.1f}, {self.offset_y:.1f}))"
        )
