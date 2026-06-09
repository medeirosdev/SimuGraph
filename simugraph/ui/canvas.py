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

    def draw(self, camera: Camera, graph: Graph, edge_start_node: Node | None = None, selection_box: tuple[int, int, int, int] | None = None) -> None:
        """Clear the surface and redraw everything for one frame."""
        self.surface.fill((0, 0, 0, 0))
        self._draw_grid(camera)
        self._draw_edges(camera, graph, edge_start_node)
        self._draw_nodes(camera, graph)
        if selection_box:
            self._draw_selection_box(selection_box)

    def _draw_selection_box(self, box: tuple[int, int, int, int]) -> None:
        """Draws screen-space click-drag selection box overlay."""
        x1, y1, x2, y2 = box
        rx, ry = min(x1, x2), min(y1, y2)
        rw, rh = abs(x2 - x1), abs(y2 - y1)
        if rw > 0 and rh > 0:
            box_rect = pygame.Rect(rx, ry, rw, rh)
            # Create transparent surface for box fill
            fill_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            fill_surf.fill(cfg.THEME["selection_box"])
            self.surface.blit(fill_surf, (rx, ry))
            # Border
            pygame.draw.rect(self.surface, cfg.THEME["selection_border"], box_rect, width=1)

    def _draw_edges(self, camera: Camera, graph: Graph, edge_start_node: Node | None = None) -> None:
        """Draw all edges in the graph using straight or Bezier curves for parallel edges."""
        import math
        from collections import defaultdict

        # Group edges by endpoints (unordered pair) to identify parallel/bidirectional connections
        edge_groups = defaultdict(list)
        for edge in graph.edges():
            key = tuple(sorted([edge.u, edge.v]))
            edge_groups[key].append(edge)

        # Draw existing edges
        for (u_id, v_id), edges_list in edge_groups.items():
            u_node = graph.get_node(u_id)
            v_node = graph.get_node(v_id)
            if not u_node or not v_node:
                continue

            su_x, sy_u = camera.world_to_screen(u_node.x, u_node.y)
            sv_x, sy_v = camera.world_to_screen(v_node.x, v_node.y)

            num_edges = len(edges_list)
            for idx, edge in enumerate(edges_list):
                # Calculate color
                color = cfg.THEME["edge_directed"] if (edge.directed and not edge.selected) else (cfg.THEME["edge_selected"] if edge.selected else edge.color)

                # Determine curve offset: if only 1 edge, straight line. Otherwise offset curves.
                if num_edges == 1:
                    # Straight line
                    pygame.draw.line(self.surface, color, (su_x, sy_u), (sv_x, sy_v), 2)
                    
                    mid_x = (su_x + sv_x) / 2
                    mid_y = (sy_u + sy_v) / 2
                    
                    # Arrowhead direction
                    dx = sv_x - su_x
                    dy = sy_v - sy_u
                    angle = math.atan2(dy, dx)
                    
                    # Target node boundary for arrow
                    target_node = v_node if edge.v == v_id else u_node
                    target_x, target_y = (sv_x, sy_v) if edge.v == v_id else (su_x, sy_u)
                else:
                    # Quadratic Bezier: P(t) = (1-t)^2 * A + 2(1-t)t * C + t^2 * B
                    # Control point C is offset from the midpoint of AB along normal vector
                    mid_x = (su_x + sv_x) / 2
                    mid_y = (sy_u + sy_v) / 2
                    
                    dx = sv_x - su_x
                    dy = sy_v - sy_u
                    length = (dx**2 + dy**2)**0.5
                    
                    if length > 0:
                        nx = -dy / length
                        ny = dx / length
                    else:
                        nx, ny = 0, 0
                    
                    # Curvature spacing (scale with camera zoom for consistent screen distance)
                    spacing = 25.0 * max(0.5, min(2.0, camera.zoom))
                    offset = (idx - (num_edges - 1) / 2) * spacing
                    
                    cx = mid_x + offset * nx
                    cy = mid_y + offset * ny
                    
                    # Calculate curve points
                    steps = 15
                    points = []
                    for s in range(steps + 1):
                        t = s / steps
                        px = (1 - t)**2 * su_x + 2 * (1 - t) * t * cx + t**2 * sv_x
                        py = (1 - t)**2 * sy_u + 2 * (1 - t) * t * cy + t**2 * sy_v
                        points.append((px, py))
                    
                    pygame.draw.lines(self.surface, color, False, points, 2)
                    
                    # Midpoint of the curve is P(0.5)
                    mid_x = 0.25 * su_x + 0.5 * cx + 0.25 * sv_x
                    mid_y = 0.25 * sy_u + 0.5 * cy + 0.25 * sy_v
                    
                    # Arrowhead direction (tangent at t=0.9)
                    t_arrow = 0.9
                    # Derivative of P(t) is 2(1-t)(C - A) + 2t(B - C)
                    tx = 2 * (1 - t_arrow) * (cx - su_x) + 2 * t_arrow * (sv_x - cx)
                    ty = 2 * (1 - t_arrow) * (cy - sy_u) + 2 * t_arrow * (sy_v - cy)
                    angle = math.atan2(ty, tx)
                    
                    # Target node boundary for arrow
                    target_node = v_node if edge.v == v_id else u_node
                    target_x, target_y = (sv_x, sy_v) if edge.v == v_id else (su_x, sy_u)

                # Draw edge weight
                weight_str = f"{edge.weight:.1f}" if edge.weight % 1 != 0 else f"{int(edge.weight)}"
                if not hasattr(self, "font_weight"):
                    try:
                        self.font_weight = pygame.font.Font(cfg.FONT_MONO_PATH, 11)
                    except FileNotFoundError:
                        self.font_weight = pygame.font.SysFont("monospace", 11)

                text_surf = self.font_weight.render(weight_str, True, cfg.THEME["edge_weight_text"])
                tw, th = text_surf.get_size()
                bg_rect = pygame.Rect(mid_x - tw/2 - 4, mid_y - th/2 - 2, tw + 8, th + 4)
                pygame.draw.rect(self.surface, cfg.THEME["edge_weight_bg"], bg_rect, border_radius=4)
                pygame.draw.rect(self.surface, cfg.THEME["panel_border"], bg_rect, width=1, border_radius=4)
                self.surface.blit(text_surf, (mid_x - tw/2, mid_y - th/2))

                # Draw arrowhead for directed edges
                if edge.directed:
                    # Intersect boundary of the target node
                    target_radius = max(4.0, target_node.radius * camera.zoom)
                    tx = target_x - math.cos(angle) * target_radius
                    ty = target_y - math.sin(angle) * target_radius

                    # Calculate wing tips
                    arrow_len = max(6.0, 10.0 * camera.zoom)
                    arrow_len = min(15.0, arrow_len)
                    arrow_angle = 0.4
                    
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

            # Render node weight/cost if non-zero
            if node.weight != 0.0:
                weight_str = f"{node.weight:.1f}" if node.weight % 1 != 0 else f"{int(node.weight)}"
                if not hasattr(self, "font_weight"):
                    try:
                        self.font_weight = pygame.font.Font(cfg.FONT_MONO_PATH, 11)
                    except FileNotFoundError:
                        self.font_weight = pygame.font.SysFont("monospace", 11)
                
                # Small badge above the node
                w_surf = self.font_weight.render(weight_str, True, cfg.THEME["edge_weight_text"])
                ww, wh = w_surf.get_size()
                wx_pos = sx
                wy_pos = sy - s_radius - wh/2 - 6
                
                bg_rect = pygame.Rect(wx_pos - ww/2 - 4, wy_pos - wh/2 - 2, ww + 8, wh + 4)
                pygame.draw.rect(self.surface, cfg.THEME["edge_weight_bg"], bg_rect, border_radius=4)
                pygame.draw.rect(self.surface, cfg.THEME["panel_border"], bg_rect, width=1, border_radius=4)
                self.surface.blit(w_surf, (wx_pos - ww/2, wy_pos - wh/2))


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
