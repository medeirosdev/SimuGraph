"""
Canvas — draws the infinite grid and will host all graph rendering.

The grid lines are spaced every GRID_MINOR world-units, with a major line
every GRID_MAJOR_FACTOR minor lines. Camera offset and zoom are applied via
the Camera instance so the grid scrolls and scales correctly.
"""

from __future__ import annotations
import pygame
import math
import simugraph.settings as cfg
from simugraph.camera import Camera
from simugraph.core.graph import Graph
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simugraph.algorithms.base import AlgoState
    from simugraph.core.node import Node

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

    def draw(
        self,
        camera: Camera,
        graph: Graph,
        edge_start_node: Node | None = None,
        selection_box: tuple[int, int, int, int] | None = None,
        articulation_points: set[str] | None = None,
        bridges: set[str] | None = None,
        algo_state: AlgoState | None = None,
        source_node_id: str | None = None
    ) -> None:
        """Clear the surface and redraw everything for one frame."""
        self.surface.fill((0, 0, 0, 0))
        self._draw_grid(camera)
        self._draw_edges(camera, graph, edge_start_node, bridges=bridges, algo_state=algo_state)
        self._draw_nodes(camera, graph, articulation_points=articulation_points, algo_state=algo_state, source_node_id=source_node_id)
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

    def _draw_edges(
        self,
        camera: Camera,
        graph: Graph,
        edge_start_node: Node | None = None,
        bridges: set[str] | None = None,
        algo_state: AlgoState | None = None
    ) -> None:
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

            # --- Handle self-loops ---
            if u_id == v_id:
                num_edges = len(edges_list)
                for idx, edge in enumerate(edges_list):
                    # Calculate color and width
                    is_algo_highlighted = algo_state and edge.id in algo_state.highlighted_edges
                    if is_algo_highlighted:
                        color = (255, 80, 160)
                        edge_w = 4
                    else:
                        color = cfg.THEME["edge_directed"] if (edge.directed and not edge.selected) else (cfg.THEME["edge_selected"] if edge.selected else edge.color)
                        edge_w = 2
                    
                    theta = -math.pi / 4  # Top-right angle
                    r = u_node.radius * camera.zoom
                    
                    # Vary loop size for nested parallel self-loops
                    loop_r = r * (0.8 + idx * 0.5)
                    loop_offset = r + loop_r - 2
                    
                    lc_x = su_x + loop_offset * math.cos(theta)
                    lc_y = sy_u + loop_offset * math.sin(theta)
                    
                    # Draw circular loop arc (pygame.draw.circle is clipped by node fill)
                    if bridges and edge.id in bridges:
                        pygame.draw.circle(self.surface, (255, 107, 107), (int(lc_x), int(lc_y)), int(loop_r), width=5)
                    pygame.draw.circle(self.surface, color, (int(lc_x), int(lc_y)), int(loop_r), width=edge_w)
                    
                    # Arrowhead for directed self-loops
                    if edge.directed:
                        arrow_angle = theta - 0.4
                        ax = su_x + r * math.cos(arrow_angle)
                        ay = sy_u + r * math.sin(arrow_angle)
                        
                        tangent_angle = math.atan2(ay - lc_y, ax - lc_x) + math.pi / 2
                        
                        arrow_len = max(6.0, 10.0 * camera.zoom)
                        arrow_len = min(15.0, arrow_len)
                        wing_angle = 0.4
                        
                        lx = ax - arrow_len * math.cos(tangent_angle - wing_angle)
                        ly = ay - arrow_len * math.sin(tangent_angle - wing_angle)
                        rx = ax - arrow_len * math.cos(tangent_angle + wing_angle)
                        ry = ay - arrow_len * math.sin(tangent_angle + wing_angle)
                        
                        pygame.draw.polygon(self.surface, color, [(ax, ay), (lx, ly), (rx, ry)])

                    # Flow particles along self-loop (LOD)
                    if camera.zoom >= 0.4:
                        t_offset = (pygame.time.get_ticks() / 1800.0) % 1.0
                        particle_color = cfg.THEME["accent"]
                        for p_idx in range(3):
                            t_val = (t_offset + p_idx / 3.0) % 1.0
                            p_angle = (theta + math.pi) + t_val * 2 * math.pi
                            px = lc_x + loop_r * math.cos(p_angle)
                            py = lc_y + loop_r * math.sin(p_angle)
                            
                            dist_node = ((px - su_x)**2 + (py - sy_u)**2)**0.5
                            if dist_node > r:
                                pygame.draw.circle(self.surface, particle_color, (int(px), int(py)), 3)

                    # Draw weight label at loop apex (LOD)
                    if camera.zoom >= 0.5:
                        weight_str = f"{edge.weight:.1f}" if edge.weight % 1 != 0 else f"{int(edge.weight)}"
                        if not hasattr(self, "font_weight"):
                            try:
                                self.font_weight = pygame.font.Font(cfg.FONT_MONO_PATH, 11)
                            except FileNotFoundError:
                                self.font_weight = pygame.font.SysFont("monospace", 11)

                        text_surf = self.font_weight.render(weight_str, True, cfg.THEME["edge_weight_text"])
                        tw, th = text_surf.get_size()
                        
                        wx_pos = lc_x + loop_r * math.cos(theta)
                        wy_pos = lc_y + loop_r * math.sin(theta)
                        
                        bg_rect = pygame.Rect(wx_pos - tw/2 - 4, wy_pos - th/2 - 2, tw + 8, th + 4)
                        pygame.draw.rect(self.surface, cfg.THEME["edge_weight_bg"], bg_rect, border_radius=4)
                        pygame.draw.rect(self.surface, cfg.THEME["panel_border"], bg_rect, width=1, border_radius=4)
                        self.surface.blit(text_surf, (wx_pos - tw/2, wy_pos - th/2))
                continue

            num_edges = len(edges_list)
            for idx, edge in enumerate(edges_list):
                # Calculate color and width
                is_algo_highlighted = algo_state and edge.id in algo_state.highlighted_edges
                if is_algo_highlighted:
                    color = (255, 80, 160)
                    edge_w = 4
                else:
                    color = cfg.THEME["edge_directed"] if (edge.directed and not edge.selected) else (cfg.THEME["edge_selected"] if edge.selected else edge.color)
                    edge_w = 2

                # Determine curve offset: if only 1 edge, straight line. Otherwise offset curves.
                if num_edges == 1:
                    # Straight line
                    if bridges and edge.id in bridges:
                        pygame.draw.line(self.surface, (255, 107, 107), (su_x, sy_u), (sv_x, sy_v), 5)
                    pygame.draw.line(self.surface, color, (su_x, sy_u), (sv_x, sy_v), edge_w)
                    
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
                    
                    if bridges and edge.id in bridges:
                        pygame.draw.lines(self.surface, (255, 107, 107), False, points, 5)
                    pygame.draw.lines(self.surface, color, False, points, edge_w)
                    
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

                # Draw flow particles along the edge trajectory (LOD: skip if zoomed out far)
                if camera.zoom >= 0.4:
                    t_offset = (pygame.time.get_ticks() / 1800.0) % 1.0
                    particle_color = cfg.THEME["accent"]
                    u_radius_px = u_node.radius * camera.zoom
                    v_radius_px = v_node.radius * camera.zoom
                    for i in range(3):
                        t_val = (t_offset + i / 3.0) % 1.0
                        # Align flow direction from edge.u to edge.v
                        if edge.u == v_id:
                            t_val = 1.0 - t_val

                        if num_edges == 1:
                            px = su_x * (1 - t_val) + sv_x * t_val
                            py = sy_u * (1 - t_val) + sy_v * t_val
                        else:
                            px = (1 - t_val)**2 * su_x + 2 * (1 - t_val) * t_val * cx + t_val**2 * sv_x
                            py = (1 - t_val)**2 * sy_u + 2 * (1 - t_val) * t_val * cy + t_val**2 * sy_v
                        
                        dist_u = ((px - su_x)**2 + (py - sy_u)**2)**0.5
                        dist_v = ((px - sv_x)**2 + (py - sy_v)**2)**0.5
                        
                        if dist_u > u_radius_px and dist_v > v_radius_px:
                            pygame.draw.circle(self.surface, particle_color, (int(px), int(py)), 3)

                # Draw edge weight (LOD: skip if zoomed out far)
                if camera.zoom >= 0.5:
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

    def _draw_nodes(
        self,
        camera: Camera,
        graph: Graph,
        articulation_points: set[str] | None = None,
        algo_state: AlgoState | None = None,
        source_node_id: str | None = None
    ) -> None:
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

            if algo_state and node.id in algo_state.visited:
                fill_color = (80, 220, 120)
                stroke_color = cfg.THEME["node_stroke"]
            elif algo_state and node.id in algo_state.frontier:
                fill_color = (255, 160, 60)
                stroke_color = cfg.THEME["node_stroke"]
            elif node.selected:
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

            if node.id == source_node_id:
                stroke_color = (80, 180, 255)

            # If selected, draw animated selection glow behind the node
            if node.selected:
                t_msec = pygame.time.get_ticks()
                pulse = (math.sin(t_msec / 180.0) + 1.0) / 2.0  # 0.0 to 1.0
                base_color = cfg.THEME["node_selected"]
                for i in range(4):
                    radius_offset = 2 + i * 3 + pulse * 4
                    alpha = int((4 - i) * 30 * (1.0 - pulse * 0.25))
                    alpha = max(0, min(255, alpha))
                    pygame.draw.circle(
                        self.surface,
                        (*base_color[:3], alpha),
                        (sx, sy),
                        int(s_radius + radius_offset),
                        width=1
                    )

            # Draw filled circle & smooth outer outline
            pygame.gfxdraw.filled_circle(self.surface, sx, sy, s_radius, fill_color)
            pygame.gfxdraw.aacircle(self.surface, sx, sy, s_radius, stroke_color)
            
            # Articulation Point indicator (glowing target ring)
            if articulation_points and node.id in articulation_points:
                pygame.draw.circle(self.surface, (255, 204, 0), (sx, sy), s_radius + 5, width=2)
            
            # Subtle inner ring if selected
            if node.selected:
                pygame.gfxdraw.aacircle(self.surface, sx, sy, max(1, s_radius - 2), (20, 20, 20))

            # Render text label (Level of Detail: omit if zoomed out too far)
            if node.label and camera.zoom >= 0.3:
                text_surf = self.font_node.render(node.label, True, cfg.THEME["node_label"])
                text_rect = text_surf.get_rect(center=(sx, sy))
                self.surface.blit(text_surf, text_rect)

            # Render node distance or node weight/cost (Level of Detail: omit if zoomed out)
            if camera.zoom >= 0.45:
                badge_str = None
                if algo_state and algo_state.distances and node.id in algo_state.distances:
                    dist_val = algo_state.distances[node.id]
                    if dist_val == float('inf'):
                        badge_str = "d: inf"
                    else:
                        badge_str = f"d: {dist_val:.1f}" if dist_val % 1 != 0 else f"d: {int(dist_val)}"
                elif node.weight != 0.0:
                    badge_str = f"{node.weight:.1f}" if node.weight % 1 != 0 else f"{int(node.weight)}"

                if badge_str is not None:
                    if not hasattr(self, "font_weight"):
                        try:
                            self.font_weight = pygame.font.Font(cfg.FONT_MONO_PATH, 11)
                        except FileNotFoundError:
                            self.font_weight = pygame.font.SysFont("monospace", 11)
                    
                    w_surf = self.font_weight.render(badge_str, True, cfg.THEME["edge_weight_text"])
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
