"""
Toolbar UI component — handles top menu bars and dropdown selections.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg


class Toolbar:
    """
    Horizontal menu bar at the top of the window.
    Height is configured in settings (cfg.TOOLBAR_H).
    """

    def __init__(self) -> None:
        self.height = cfg.TOOLBAR_H
        self.rect = pygame.Rect(0, 0, cfg.WINDOW_W, self.height)
        
        # Menu definitions: (id, label, rect, items)
        # items are list of (item_id, item_label)
        self.menus = [
            {
                "id": "file",
                "label": "File",
                "rect": pygame.Rect(10, 4, 60, self.height - 8),
                "items": [
                    ("open", "Open... (Ctrl+O)"),
                    ("save", "Save (Ctrl+S)"),
                    ("clear", "Clear Graph"),
                    ("exit", "Exit"),
                ]
            },
            {
                "id": "algo",
                "label": "Algorithms",
                "rect": pygame.Rect(80, 4, 110, self.height - 8),
                "items": [
                    ("bfs", "Breadth-First Search (BFS)"),
                    ("dfs", "Depth-First Search (DFS)"),
                    ("dijkstra", "Dijkstra's Algorithm"),
                    ("scc", "SCC Color Coding"),
                ]
            },
            {
                "id": "generate",
                "label": "Generate",
                "rect": pygame.Rect(200, 4, 90, self.height - 8),
                "items": [
                    ("gen_random", "Random Graph..."),
                    ("gen_complete", "Complete Graph..."),
                ]
            }
        ]
        
        self.active_menu_id: str | None = None
        self.dropdown_rect: pygame.Rect | None = None

        # Cache font
        try:
            self.font = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw background panel
        bg_color = cfg.THEME["toolbar_bg"]
        border_color = cfg.THEME["panel_border"]
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.line(surface, border_color, (0, self.height - 1), (cfg.WINDOW_W, self.height - 1), 1)

        mx, my = pygame.mouse.get_pos()

        # Draw menu headers
        for menu in self.menus:
            is_hover = menu["rect"].collidepoint(mx, my)
            is_active = (menu["id"] == self.active_menu_id)

            if is_active:
                header_bg = cfg.THEME["panel_border"]
                text_color = cfg.THEME["accent"]
            elif is_hover:
                header_bg = cfg.THEME["panel_border"]
                text_color = cfg.THEME["text"]
            else:
                header_bg = cfg.THEME["toolbar_bg"]
                text_color = cfg.THEME["text_dim"]

            if is_hover or is_active:
                pygame.draw.rect(surface, header_bg, menu["rect"], border_radius=4)

            # Draw text centered
            text_surf = self.font.render(menu["label"], True, text_color)
            text_rect = text_surf.get_rect(center=menu["rect"].center)
            surface.blit(text_surf, text_rect)

        # Draw active dropdown
        if self.active_menu_id:
            menu = next(m for m in self.menus if m["id"] == self.active_menu_id)
            items = menu["items"]
            
            # Determine size of dropdown
            max_w = 200
            for _, item_lbl in items:
                lbl_w = self.font.size(item_lbl)[0]
                if lbl_w + 30 > max_w:
                    max_w = lbl_w + 30

            row_h = 30
            dropdown_h = len(items) * row_h + 8
            
            # Position dropdown below header
            x = menu["rect"].x
            y = self.height
            
            self.dropdown_rect = pygame.Rect(x, y, max_w, dropdown_h)
            
            # Draw shadow
            shadow_rect = self.dropdown_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(surface, (10, 10, 15, 100), shadow_rect, border_radius=6)
            
            # Draw dropdown border & background
            pygame.draw.rect(surface, cfg.THEME["context_bg"], self.dropdown_rect, border_radius=6)
            pygame.draw.rect(surface, cfg.THEME["panel_border"], self.dropdown_rect, width=1, border_radius=6)

            # Draw dropdown items
            for idx, (item_id, item_lbl) in enumerate(items):
                item_y = y + 4 + idx * row_h
                item_rect = pygame.Rect(x + 4, item_y, max_w - 8, row_h)
                
                is_item_hover = item_rect.collidepoint(mx, my)
                if is_item_hover:
                    pygame.draw.rect(surface, cfg.THEME["context_hover"], item_rect, border_radius=4)
                    item_text_color = cfg.THEME["text"]
                else:
                    item_text_color = cfg.THEME["text_dim"]

                # Render label
                lbl_surf = self.font.render(item_lbl, True, item_text_color)
                surface.blit(lbl_surf, (item_rect.x + 10, item_rect.y + (row_h - lbl_surf.get_height()) // 2))

    def handle_click(self, mx: int, my: int) -> tuple[str, str] | None:
        """
        Processes click.
        Returns (menu_id, action_id) if dropdown action selected.
        Toggles active menu if menu headers clicked.
        Closes dropdown if click outside.
        """
        # 1. Check if dropdown item was clicked
        if self.active_menu_id and self.dropdown_rect and self.dropdown_rect.collidepoint(mx, my):
            menu = next(m for m in self.menus if m["id"] == self.active_menu_id)
            row_h = 30
            idx = (my - (self.height + 4)) // row_h
            if 0 <= idx < len(menu["items"]):
                action_id = menu["items"][idx][0]
                clicked_menu = self.active_menu_id
                self.active_menu_id = None
                self.dropdown_rect = None
                return (clicked_menu, action_id)
            
        # 2. Check if menu header clicked
        for menu in self.menus:
            if menu["rect"].collidepoint(mx, my):
                if self.active_menu_id == menu["id"]:
                    self.active_menu_id = None
                    self.dropdown_rect = None
                else:
                    self.active_menu_id = menu["id"]
                return None

        # 3. Clicked outside active dropdown, close it
        if self.active_menu_id:
            self.active_menu_id = None
            self.dropdown_rect = None
            
        return None
