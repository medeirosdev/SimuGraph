"""
HUD (Heads-Up Display) / Status Bar UI component.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg
from simugraph.core.graph import Graph
from simugraph.camera import Camera


class HUD:
    """
    Bottom status bar showing application status: active tool,
    snapping, edge type, graph sizes, camera zoom level, active theme, and FPS.
    """

    def __init__(self) -> None:
        self.height = cfg.HUD_H
        self.rect = pygame.Rect(0, cfg.WINDOW_H - self.height, cfg.WINDOW_W, self.height)
        
        self.reload_fonts()

    def reload_fonts(self) -> None:
        try:
            self.font = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_HUD)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("monospace", cfg.FONT_SIZE_HUD)

    def draw(self, surface: pygame.Surface, active_tool: str, snap_enabled: bool, directed_edges: bool, graph: Graph, camera: Camera, fps: float) -> None:
        # Create sub-surface for transparency
        hud_surf = pygame.Surface((cfg.WINDOW_W, self.height), pygame.SRCALPHA)
        hud_surf.fill(cfg.THEME["hud_bg"])

        # Compose status text parts
        tool_txt = f"TOOL: {active_tool.upper()}"
        snap_txt = f"SNAP: {'ON' if snap_enabled else 'OFF'}"
        dir_txt = f"DIR: {'ON' if directed_edges else 'OFF'}"
        stats_txt = f"NODES: {graph.node_count()}  EDGES: {graph.edge_count()}"
        zoom_txt = f"ZOOM: {camera.zoom_percent()}%"
        theme_txt = f"THEME: {cfg.ACTIVE_THEME_NAME.upper()}"
        fps_txt = f"FPS: {fps:.0f}"

        # Combine text segments with elegant separators
        full_text = f"  {tool_txt}  |  {snap_txt}  |  {dir_txt}  |  {stats_txt}  |  {zoom_txt}  |  {theme_txt}  |  {fps_txt}"
        
        # Render text
        text_surf = self.font.render(full_text, True, cfg.THEME["text_dim"])
        y_pos = (self.height - text_surf.get_height()) // 2
        hud_surf.blit(text_surf, (10, y_pos))

        # Blit onto main surface
        surface.blit(hud_surf, (0, cfg.WINDOW_H - self.height))
