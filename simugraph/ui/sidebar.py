"""
Sidebar UI component — contains tool selection buttons.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg


class Sidebar:
    """
    Vertical panel on the left containing action tools.
    Width is configured in settings (cfg.SIDEBAR_W).
    """

    def __init__(self) -> None:
        self.width = cfg.SIDEBAR_W
        self.height = cfg.WINDOW_H - cfg.HUD_H  # starts below toolbar, but for now takes full height minus HUD
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        
        # Define buttons (id, tooltip, icon_draw_fn)
        self.buttons = [
            ("select", "Select/Move (V)"),
            ("node", "Add Node (N)"),
            ("edge", "Add Edge (E)"),
            ("remove", "Remove Tool (R)"),
        ]
        self.btn_height = 60
        self.padding = 10

    def draw(self, surface: pygame.Surface, active_tool: str) -> None:
        # Draw background panel
        bg_color = cfg.THEME["sidebar_bg"]
        border_color = cfg.THEME["panel_border"]
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.line(surface, border_color, (self.width - 1, 0), (self.width - 1, self.height), 1)

        # Draw buttons
        for i, (tool_id, tooltip) in enumerate(self.buttons):
            btn_y = cfg.TOOLBAR_H + i * (self.btn_height + self.padding) + self.padding
            btn_rect = pygame.Rect(self.padding, btn_y, self.width - 2 * self.padding, self.btn_height)
            
            # Hover / Active styling
            mx, my = pygame.mouse.get_pos()
            is_hover = btn_rect.collidepoint(mx, my)
            is_active = (tool_id == active_tool)

            if is_active:
                btn_color = cfg.THEME["accent"]
                icon_color = cfg.THEME["sidebar_bg"]
            elif is_hover:
                btn_color = cfg.THEME["panel_border"]
                icon_color = cfg.THEME["text"]
            else:
                btn_color = cfg.THEME["sidebar_bg"]
                icon_color = cfg.THEME["text_dim"]

            # Draw button background
            if is_active or is_hover:
                pygame.draw.rect(surface, btn_color, btn_rect, border_radius=6)
                if is_active:
                    # Draw a small accent strip on the left edge
                    pygame.draw.rect(surface, cfg.THEME["accent"], (0, btn_y, 4, self.btn_height))

            # Draw icons using primitives
            cx, cy = btn_rect.center
            if tool_id == "select":
                # Draw cursor arrow icon
                pygame.draw.polygon(surface, icon_color, [
                    (cx - 6, cy - 8),
                    (cx + 6, cy + 4),
                    (cx, cy + 6),
                    (cx - 6, cy + 10)
                ])
            elif tool_id == "node":
                # Draw node circle icon
                pygame.draw.circle(surface, icon_color, (cx, cy), 8, 2)
                pygame.draw.circle(surface, icon_color, (cx, cy), 3)
            elif tool_id == "edge":
                # Draw connection line icon
                pygame.draw.circle(surface, icon_color, (cx - 7, cy + 7), 4, 1)
                pygame.draw.circle(surface, icon_color, (cx + 7, cy - 7), 4, 1)
                pygame.draw.line(surface, icon_color, (cx - 5, cy + 5), (cx + 5, cy - 5), 2)
            elif tool_id == "remove":
                # Draw trashcan or X icon
                pygame.draw.line(surface, icon_color, (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
                pygame.draw.line(surface, icon_color, (cx + 6, cy - 6), (cx - 6, cy + 6), 2)

    def handle_click(self, mx: int, my: int) -> str | None:
        """Checks if a sidebar button was clicked and returns the tool_id."""
        if not self.rect.collidepoint(mx, my):
            return None

        for i, (tool_id, _) in enumerate(self.buttons):
            btn_y = cfg.TOOLBAR_H + i * (self.btn_height + self.padding) + self.padding
            btn_rect = pygame.Rect(self.padding, btn_y, self.width - 2 * self.padding, self.btn_height)
            if btn_rect.collidepoint(mx, my):
                return tool_id
        return None
