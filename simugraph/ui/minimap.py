from __future__ import annotations
import pygame
import simugraph.settings as cfg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph
    from simugraph.camera import Camera

class Minimap:
    def __init__(self) -> None:
        self.width = cfg.MINIMAP_W
        self.height = cfg.MINIMAP_H
        self.margin = cfg.MINIMAP_MARGIN
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.is_dragging = False

    def update_position(self) -> None:
        # Position at the bottom-right corner of the canvas (left of inspector, above HUD)
        self.rect.x = cfg.WINDOW_W - cfg.INSPECTOR_W - self.width - self.margin
        self.rect.y = cfg.WINDOW_H - cfg.HUD_H - self.height - self.margin

    def draw(self, surface: pygame.Surface, graph: Graph, camera: Camera) -> None:
        self.update_position()
        
        # Transparent background panel
        panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surf.fill(cfg.THEME.get("minimap_bg", (15, 15, 25, 200)))
        pygame.draw.rect(panel_surf, cfg.THEME.get("minimap_border", (60, 65, 90)), (0, 0, self.width, self.height), width=1, border_radius=6)
        
        nodes = list(graph.nodes())
        if not nodes:
            surface.blit(panel_surf, self.rect)
            return

        # Calculate bounding box of all nodes
        xs = [n.x for n in nodes]
        ys = [n.y for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Add a minimum bounding box size to avoid division by zero or extreme scaling
        span_x = max(800.0, max_x - min_x)
        span_y = max(600.0, max_y - min_y)
        
        # Center of bounding box
        cx = min_x + (max_x - min_x) / 2
        cy = min_y + (max_y - min_y) / 2
        
        # Scale factor to fit graph in minimap with 10% padding
        scale = min((self.width - 20) / span_x, (self.height - 20) / span_y)
        
        # Helper to transform world space to minimap pixel space
        def world_to_minimap(wx: float, wy: float) -> tuple[float, float]:
            mx = self.width / 2 + (wx - cx) * scale
            my = self.height / 2 + (wy - cy) * scale
            return mx, my

        # Draw edges
        edge_color = cfg.THEME.get("edge", (150, 155, 185))
        for edge in graph.edges():
            u_node = graph.get_node(edge.u)
            v_node = graph.get_node(edge.v)
            if u_node and v_node:
                ux, uy = world_to_minimap(u_node.x, u_node.y)
                vx, vy = world_to_minimap(v_node.x, v_node.y)
                pygame.draw.line(panel_surf, edge_color, (ux, uy), (vx, vy), 1)
                
        # Draw nodes
        node_color = cfg.THEME.get("node_fill", (60, 130, 220))
        for node in nodes:
            nx, ny = world_to_minimap(node.x, node.y)
            pygame.draw.circle(panel_surf, node_color, (int(nx), int(ny)), 2)

        # Draw viewport rectangle
        canvas_w = cfg.WINDOW_W - cfg.INSPECTOR_W - cfg.SIDEBAR_W
        canvas_h = cfg.WINDOW_H - cfg.TOOLBAR_H - cfg.HUD_H
        
        # Viewport coordinates in world space
        v_world_x1 = (cfg.SIDEBAR_W - camera.x) / camera.zoom
        v_world_y1 = (cfg.TOOLBAR_H - camera.y) / camera.zoom
        v_world_x2 = v_world_x1 + canvas_w / camera.zoom
        v_world_y2 = v_world_y1 + canvas_h / camera.zoom
        
        vx1, vy1 = world_to_minimap(v_world_x1, v_world_y1)
        vx2, vy2 = world_to_minimap(v_world_x2, v_world_y2)
        
        # Clamp viewport to minimap bounds
        vx1_c = max(0, min(self.width, vx1))
        vy1_c = max(0, min(self.height, vy1))
        vx2_c = max(0, min(self.width, vx2))
        vy2_c = max(0, min(self.height, vy2))
        
        v_rect = pygame.Rect(vx1_c, vy1_c, max(4, vx2_c - vx1_c), max(4, vy2_c - vy1_c))
        
        # Semi-transparent viewport fill
        vp_fill_surf = pygame.Surface((v_rect.width, v_rect.height), pygame.SRCALPHA)
        vp_fill_surf.fill(cfg.THEME.get("minimap_viewport", (90, 160, 255, 80)))
        panel_surf.blit(vp_fill_surf, v_rect)
        pygame.draw.rect(panel_surf, cfg.THEME.get("selection_border", (90, 160, 255)), v_rect, width=1)
        
        surface.blit(panel_surf, self.rect)

    def handle_click(self, mx: int, my: int, graph: Graph, camera: Camera) -> bool:
        """
        Check if click is inside minimap.
        If yes, pan the camera to center on the clicked spot.
        """
        self.update_position()
        if not self.rect.collidepoint(mx, my):
            return False
            
        nodes = list(graph.nodes())
        if not nodes:
            return True
            
        # Get click position relative to minimap top-left
        rx = mx - self.rect.x
        ry = my - self.rect.y
        
        # Reverse map rx, ry to world space coordinates
        xs = [n.x for n in nodes]
        ys = [n.y for n in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        span_x = max(800.0, max_x - min_x)
        span_y = max(600.0, max_y - min_y)
        cx = min_x + (max_x - min_x) / 2
        cy = min_y + (max_y - min_y) / 2
        
        scale = min((self.width - 20) / span_x, (self.height - 20) / span_y)
        
        world_x = cx + (rx - self.width / 2) / scale
        world_y = cy + (ry - self.height / 2) / scale
        
        # Center camera on world_x, world_y
        canvas_w = cfg.WINDOW_W - cfg.INSPECTOR_W - cfg.SIDEBAR_W
        canvas_h = cfg.WINDOW_H - cfg.TOOLBAR_H - cfg.HUD_H
        screen_cx = cfg.SIDEBAR_W + canvas_w / 2
        screen_cy = cfg.TOOLBAR_H + canvas_h / 2
        
        camera.x = screen_cx - world_x * camera.zoom
        camera.y = screen_cy - world_y * camera.zoom
        
        self.is_dragging = True
        return True
