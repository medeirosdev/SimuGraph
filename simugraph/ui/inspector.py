"""
Inspector UI component — displays properties of the selected node or edge.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
import simugraph.settings as cfg
from simugraph.ui.properties_panel import PropertiesPanel

if TYPE_CHECKING:
    from simugraph.core.node import Node
    from simugraph.core.edge import Edge
    from simugraph.core.graph import Graph


class Inspector:
    """
    Vertical panel on the right displaying and editing properties
    of the currently selected node or edge.
    """

    def __init__(self) -> None:
        self.width = cfg.INSPECTOR_W
        self.x = cfg.WINDOW_W - self.width
        self.y = cfg.TOOLBAR_H
        self.height = cfg.WINDOW_H - cfg.TOOLBAR_H - cfg.HUD_H
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.reload_fonts()

    def reload_fonts(self) -> None:
        try:
            self.font_title = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_HUD)
            self.font_body = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font_title = pygame.font.SysFont("monospace", cfg.FONT_SIZE_HUD)
            self.font_body = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)
        if hasattr(self, "properties_panel"):
            self.properties_panel.reload_fonts()

        # Interactive rects
        self.pin_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.color_rects: list[tuple[pygame.Color, pygame.Rect]] = []
        self.export_button_rect = pygame.Rect(0, 0, 0, 0)
        self.properties_panel = PropertiesPanel(self.x, self.y, self.width)

    def draw(self, surface: pygame.Surface, graph: Graph, selected_node: Node | None, selected_edge: Edge | None, algo_runner: Any | None = None, centrality_mode: str | None = None) -> None:
        # Clear interactive rects
        self.pin_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.color_rects.clear()
        self.export_button_rect = pygame.Rect(0, 0, 0, 0)

        # Draw panel background & border
        bg_color = cfg.THEME["sidebar_bg"]
        border_color = cfg.THEME["panel_border"]
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.line(surface, border_color, (self.x, self.y), (self.x, self.y + self.height), 1)

        # Draw Header
        header_text = self.font_title.render("INSPECTOR", True, cfg.THEME["text"])
        surface.blit(header_text, (self.x + 15, self.y + 15))
        pygame.draw.line(surface, border_color, (self.x + 15, self.y + 40), (self.x + self.width - 15, self.y + 40), 1)

        # Check selection state / algorithm runner
        if algo_runner and algo_runner.algorithm:
            self._draw_algorithm_properties(surface, algo_runner)
        elif selected_node:
            self._draw_node_properties(surface, selected_node)
        elif selected_edge:
            self._draw_edge_properties(surface, selected_edge)
        else:
            self.properties_panel.draw(surface, graph, centrality_mode)

    def _draw_node_properties(self, surface: pygame.Surface, node: Node) -> None:
        y_offset = self.y + 60
        text_color = cfg.THEME["text"]
        dim_color = cfg.THEME["text_dim"]

        # Label / Name
        label_title = self.font_body.render(f"Node: {node.label}", True, cfg.THEME["accent"])
        surface.blit(label_title, (self.x + 15, y_offset))
        y_offset += 25

        # ID (truncated)
        id_text = self.font_body.render(f"ID: {node.id[:8]}...", True, dim_color)
        surface.blit(id_text, (self.x + 15, y_offset))
        y_offset += 30

        # Position (World X, Y)
        pos_title = self.font_body.render("Position:", True, dim_color)
        surface.blit(pos_title, (self.x + 15, y_offset))
        y_offset += 20
        pos_val = self.font_body.render(f" X: {node.x:.1f}\n Y: {node.y:.1f}", True, text_color)
        self._render_multiline_text(surface, f" X: {node.x:.1f}\n Y: {node.y:.1f}", self.x + 15, y_offset, text_color)
        y_offset += 45

        # Pinned state (Toggle button)
        pin_title = self.font_body.render("Pinned:", True, dim_color)
        surface.blit(pin_title, (self.x + 15, y_offset))
        
        # Draw toggle button
        self.pin_toggle_rect = pygame.Rect(self.x + 90, y_offset - 2, 60, 22)
        toggle_bg = cfg.THEME["accent"] if node.pinned else cfg.THEME["panel_border"]
        toggle_text = "YES" if node.pinned else "NO"
        toggle_txt_color = cfg.THEME["sidebar_bg"] if node.pinned else cfg.THEME["text"]

        pygame.draw.rect(surface, toggle_bg, self.pin_toggle_rect, border_radius=4)
        lbl = self.font_body.render(toggle_text, True, toggle_txt_color)
        surface.blit(lbl, lbl.get_rect(center=self.pin_toggle_rect.center))
        
        y_offset += 35

        # Node weight (Edit button)
        weight_title = self.font_body.render("Weight:", True, dim_color)
        surface.blit(weight_title, (self.x + 15, y_offset))
        
        # Draw Edit button
        self.weight_edit_rect = pygame.Rect(self.x + 90, y_offset - 2, 60, 22)
        pygame.draw.rect(surface, cfg.THEME["panel_border"], self.weight_edit_rect, border_radius=4)
        w_text = f"{node.weight:.1f}" if node.weight % 1 != 0 else f"{int(node.weight)}"
        w_lbl = self.font_body.render(w_text, True, cfg.THEME["text"])
        surface.blit(w_lbl, w_lbl.get_rect(center=self.weight_edit_rect.center))

        y_offset += 40

        # Node Color Picker
        color_title = self.font_body.render("Color Preset:", True, dim_color)
        surface.blit(color_title, (self.x + 15, y_offset))
        y_offset += 25

        # Define some premium color palette options
        palette = [
            pygame.Color(220, 60, 60),    # Red
            pygame.Color(60, 180, 220),   # Cyan/Blue
            pygame.Color(60, 220, 100),   # Green
            pygame.Color(220, 180, 60),   # Gold
            pygame.Color(180, 60, 220),   # Purple
        ]

        # Draw colors
        for i, color in enumerate(palette):
            cx = self.x + 15 + i * 32
            cy = y_offset
            c_rect = pygame.Rect(cx, cy, 24, 24)
            self.color_rects.append((color, c_rect))
            
            # Check if this color matches node's current color (allowing close matching)
            is_active = (abs(node.color[0]-color.r) + abs(node.color[1]-color.g) + abs(node.color[2]-color.b)) < 10

            pygame.draw.rect(surface, color, c_rect, border_radius=4)
            if is_active:
                pygame.draw.rect(surface, cfg.THEME["text"], c_rect, width=2, border_radius=4)
            else:
                pygame.draw.rect(surface, cfg.THEME["panel_border"], c_rect, width=1, border_radius=4)

    def _draw_edge_properties(self, surface: pygame.Surface, edge: Edge) -> None:
        y_offset = self.y + 60
        text_color = cfg.THEME["text"]
        dim_color = cfg.THEME["text_dim"]

        # Label / Name
        label_title = self.font_body.render("Edge Info", True, cfg.THEME["accent"])
        surface.blit(label_title, (self.x + 15, y_offset))
        y_offset += 25

        # ID
        id_text = self.font_body.render(f"ID: {edge.id[:8]}...", True, dim_color)
        surface.blit(id_text, (self.x + 15, y_offset))
        y_offset += 30

        # Connection endpoints
        conn_title = self.font_body.render("Endpoints:", True, dim_color)
        surface.blit(conn_title, (self.x + 15, y_offset))
        y_offset += 20
        conn_val = self.font_body.render(f" From (u): {edge.u[:8]}...\n To (v):   {edge.v[:8]}...", True, text_color)
        self._render_multiline_text(surface, f" From (u): {edge.u[:8]}...\n To (v):   {edge.v[:8]}...", self.x + 15, y_offset, text_color)
        y_offset += 45

        # Directed status
        dir_title = self.font_body.render(f"Directed: {'YES' if edge.directed else 'NO'}", True, text_color)
        surface.blit(dir_title, (self.x + 15, y_offset))
        y_offset += 30

        # Weight (Edit button)
        weight_title = self.font_body.render("Weight:", True, dim_color)
        surface.blit(weight_title, (self.x + 15, y_offset))
        
        # Draw edit button
        self.edge_weight_edit_rect = pygame.Rect(self.x + 90, y_offset - 2, 60, 22)
        pygame.draw.rect(surface, cfg.THEME["panel_border"], self.edge_weight_edit_rect, border_radius=4)
        ew_text = f"{edge.weight:.1f}" if edge.weight % 1 != 0 else f"{int(edge.weight)}"
        ew_lbl = self.font_body.render(ew_text, True, cfg.THEME["text"])
        surface.blit(ew_lbl, ew_lbl.get_rect(center=self.edge_weight_edit_rect.center))

    def _render_multiline_text(self, surface: pygame.Surface, text: str, x: int, y: int, color: pygame.Color) -> None:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            lbl = self.font_body.render(line, True, color)
            surface.blit(lbl, (x, y + i * 20))

    def _draw_algorithm_properties(self, surface: pygame.Surface, algo_runner: Any) -> None:
        y_offset = self.y + 60
        text_color = cfg.THEME["text"]
        dim_color = cfg.THEME["text_dim"]
        accent_color = cfg.THEME["accent"]

        # Algorithm name
        name_lbl = self.font_body.render(algo_runner.algorithm.name, True, accent_color)
        surface.blit(name_lbl, (self.x + 15, y_offset))
        y_offset += 25

        # Step count
        curr_state = algo_runner.current_state
        if curr_state:
            step_lbl = self.font_body.render(f"Step {curr_state.step_index} / {curr_state.total_steps}", True, text_color)
            surface.blit(step_lbl, (self.x + 15, y_offset))
            y_offset += 25
            
            # Status play/pause
            status_str = "Status: PLAYING" if algo_runner.playing else "Status: PAUSED"
            status_color = (80, 220, 120) if algo_runner.playing else (220, 180, 60)
            status_lbl = self.font_body.render(status_str, True, status_color)
            surface.blit(status_lbl, (self.x + 15, y_offset))
            y_offset += 25

            # Speed
            speed_lbl = self.font_body.render(f"Speed: {algo_runner.speed_fps:.1f} Hz", True, dim_color)
            surface.blit(speed_lbl, (self.x + 15, y_offset))
            y_offset += 35

            # Divider
            pygame.draw.line(surface, cfg.THEME["panel_border"], (self.x + 15, y_offset), (self.x + self.width - 15, y_offset), 1)
            y_offset += 15

            # Detail text
            detail_title = self.font_body.render("State Details:", True, accent_color)
            surface.blit(detail_title, (self.x + 15, y_offset))
            y_offset += 25
            
            self._render_multiline_text(surface, curr_state.detail_text, self.x + 15, y_offset, text_color)
            
            # Interactive Buttons (e.g. Export Results)
            self.export_button_rect = pygame.Rect(self.x + 15, self.y + self.height - 45, self.width - 30, 30)
            pygame.draw.rect(surface, cfg.THEME["panel_border"], self.export_button_rect, border_radius=6)
            exp_lbl = self.font_body.render("Export Results (.txt)", True, text_color)
            surface.blit(exp_lbl, exp_lbl.get_rect(center=self.export_button_rect.center))

    def handle_click(
        self,
        mx: int,
        my: int,
        selected_node: Node | None,
        selected_edge: Edge | None,
        algo_runner: Any | None = None
    ) -> tuple[str, Any] | None:
        """
        Processes click in inspector.
        Returns:
            ("pin", value), ("color", color_tuple), ("node_weight", None), ("edge_weight", None), ("export_results", None)
        """
        if not self.rect.collidepoint(mx, my):
            return None

        # Check export button click
        if algo_runner and algo_runner.algorithm and hasattr(self, "export_button_rect") and self.export_button_rect.collidepoint(mx, my):
            return ("export_results", None)

        # Check pin toggle click
        if selected_node and hasattr(self, "pin_toggle_rect") and self.pin_toggle_rect.collidepoint(mx, my):
            return ("pin", not selected_node.pinned)

        # Check node weight edit click
        if selected_node and hasattr(self, "weight_edit_rect") and self.weight_edit_rect.collidepoint(mx, my):
            return ("node_weight", None)

        # Check edge weight edit click
        if selected_edge and hasattr(self, "edge_weight_edit_rect") and self.edge_weight_edit_rect.collidepoint(mx, my):
            return ("edge_weight", None)

        # Check color selection click
        if selected_node:
            for color, rect in self.color_rects:
                if rect.collidepoint(mx, my):
                    return ("color", (color.r, color.g, color.b))

        # Check properties panel click
        if not selected_node and not selected_edge and (not algo_runner or not algo_runner.algorithm):
            res = self.properties_panel.handle_click(mx, my)
            if res:
                return res

        return None
