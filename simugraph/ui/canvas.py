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

    def draw(self, camera: Camera, graph: Graph, edge_start_node: Node | None = None) -> None:
        """Clear the surface and redraw everything for one frame."""
        self.surface.fill((0, 0, 0, 0))
        self._draw_grid(camera)
        self._draw_edges(camera, graph, edge_start_node)
        self._draw_nodes(camera, graph)

    def _draw_edges(self, camera: Camera, graph: Graph, edge_start_node: Node | None = None) -> None:
        """Draw all edges in the graph and the connection preview line."""
        import math
        # Draw existing edges
        for edge in graph.edges():
            u_node = graph.get_node(edge.u)
            v_node = graph.get_node(edge.v)
            if not u_node or not v_node:
                continue

            su_x, sy_u = camera.world_to_screen(u_node.x, u_node.y)
            sv_x, sy_v = camera.world_to_screen(v_node.x, v_node.y)

            # Determine color
            color = cfg.THEME["edge_directed"] if (edge.directed and not edge.selected) else (cfg.THEME["edge_selected"] if edge.selected else edge.color)

            # Simple straight line (curved parallel edges will be added in Phase 4)
            pygame.draw.line(self.surface, color, (su_x, sy_u), (sv_x, sy_v), 2)

            # Draw arrowhead for directed edges
            if edge.directed:
                dx = sv_x - su_x
                dy = sy_v - sy_u
                dist = (dx**2 + dy**2)**0.5
                if dist > 0:
                    ux = dx / dist
                    uy = dy / dist
                    # Stop at the boundary of the target node
                    target_radius = max(4.0, v_node.radius * camera.zoom)
                    tx = sv_x - ux * target_radius
                    ty = sy_v - uy * target_radius

                    # Calculate wing tips
                    angle = math.atan2(dy, dx)
                    arrow_len = max(6.0, 10.0 * camera.zoom)
                    arrow_len = min(15.0, arrow_len)  # clamp to nice size range
                    arrow_angle = 0.4 # ~23 degrees
                    
                    lx = tx - arrow_len * math.cos(angle - arrow_angle)
                    ly = ty - arrow_len * math.sin(angle - arrow_angle)
                    rx = tx - arrow_len * math.cos(angle + arrow_angle)
                    ry = ty - arrow_len * math.sin(angle + arrow_angle)

                    pygame.draw.polygon(self.surface, color, [(tx, ty), (lx, ly), (rx, ry)])

        # Draw preview line if user is connecting two nodes
        if edge_start_node:
            su_x, sy_u = camera.world_to_screen(edge_start_node.x, edge_start_node.y)
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(self.surface, (*cfg.THEME["accent"][:3], 150), (su_x, sy_u), (mx, my), 2)

    def _draw_nodes(self, camera: Camera, graph: Graph) -> None:
        """Draw all nodes in the graph using anti-aliased primitives."""
        import pygame.gfxdraw
        if not hasattr(self, "font_node"):
            try:
                self.font_node = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_NODE)
            except FileNotFoundError:
                self.font_node = pygame.font.SysFont("monospace", cfg.FONT_SIZE_NODE)

        # Get mouse position in world space for hover detection
        mx, my = pygame.mouse.get_pos()
        m_wx, m_wy = camera.screen_to_world(mx, my)

        for node in graph.nodes():
            s_radius = int(max(4.0, node.radius * camera.zoom))
            sx_float, sy_float = camera.world_to_screen(node.x, node.y)
            sx, sy = int(sx_float), int(sy_float)

            # Visibility check
            if not (0 - s_radius <= sx <= self.width + s_radius and 0 - s_radius <= sy <= self.height + s_radius):
                continue

            # Check if hovered
            dist_to_mouse = ((node.x - m_wx)**2 + (node.y - m_wy)**2)**0.5
            is_hovered = dist_to_mouse <= node.radius

            if node.selected:
                fill_color = cfg.THEME["node_selected"]
                stroke_color = cfg.THEME["node_selected"]
            elif is_hovered:
                fill_color = cfg.THEME["node_hover"]
                stroke_color = cfg.THEME["node_stroke"]
            elif node.pinned:
                fill_color = cfg.THEME["node_pinned"]
                stroke_color = cfg.THEME["node_stroke"]
            else:
                fill_color = node.color
                stroke_color = cfg.THEME["node_stroke"]

            # Draw filled circle & smooth outer outline
            pygame.gfxdraw.filled_circle(self.surface, sx, sy, s_radius, fill_color)
            pygame.gfxdraw.aacircle(self.surface, sx, sy, s_radius, stroke_color)
            
            # Subtle inner ring if selected
            if node.selected:
                pygame.gfxdraw.aacircle(self.surface, sx, sy, max(1, s_radius - 2), (20, 20, 20))

            # Render text label
            if node.label:
                text_surf = self.font_node.render(node.label, True, cfg.THEME["node_label"])
                text_rect = text_surf.get_rect(center=(sx, sy))
                self.surface.blit(text_surf, text_rect)


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
