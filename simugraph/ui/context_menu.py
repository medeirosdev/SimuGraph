"""
Right-click context menu for nodes, edges, and canvas background.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg

class ContextMenu:
    def __init__(self) -> None:
        self.visible = False
        self.x = 0
        self.y = 0
        self.width = 180
        self.item_height = 28
        self.options: list[dict] = []
        self.hovered_idx = -1
        self.active_target = None  # Node, Edge, or None (canvas background)
        
        try:
            self.font = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI - 2)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI - 2)

    def show(self, screen_x: int, screen_y: int, target: any, options: list[dict]) -> None:
        self.visible = True
        self.options = options
        self.active_target = target
        self.hovered_idx = -1
        
        h = len(options) * self.item_height
        
        # Clamp positions to screen bounds
        self.x = min(screen_x, cfg.WINDOW_W - cfg.INSPECTOR_W - self.width - 5)
        self.x = max(self.x, cfg.SIDEBAR_W + 5)
        
        self.y = min(screen_y, cfg.WINDOW_H - cfg.HUD_H - h - 5)
        self.y = max(self.y, cfg.TOOLBAR_H + 5)

    def hide(self) -> None:
        self.visible = False
        self.options = []
        self.active_target = None
        self.hovered_idx = -1

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.options:
            return
            
        h = len(self.options) * self.item_height
        
        # Draw background menu box
        menu_surf = pygame.Surface((self.width, h), pygame.SRCALPHA)
        menu_surf.fill((*cfg.THEME["context_bg"], 245))  # slight transparency
        pygame.draw.rect(menu_surf, cfg.THEME["panel_border"], (0, 0, self.width, h), width=1, border_radius=4)
        
        surface.blit(menu_surf, (self.x, self.y))
        
        # Draw items
        for idx, opt in enumerate(self.options):
            # Hover state highlight
            if idx == self.hovered_idx:
                hover_rect = pygame.Rect(self.x + 2, self.y + idx * self.item_height + 2, self.width - 4, self.item_height - 4)
                pygame.draw.rect(surface, cfg.THEME["context_hover"], hover_rect, border_radius=3)
                text_color = (255, 255, 255)
            else:
                text_color = cfg.THEME["text"]
                
            # Render item label
            lbl_surf = self.font.render(opt["label"], True, text_color)
            surface.blit(lbl_surf, (self.x + 12, self.y + idx * self.item_height + (self.item_height - lbl_surf.get_height()) // 2))

    def handle_event(self, event: pygame.event.Event, mx: int, my: int) -> bool:
        """
        Returns True if the event was consumed, False otherwise.
        """
        if not self.visible or not self.options:
            return False
            
        h = len(self.options) * self.item_height
        menu_rect = pygame.Rect(self.x, self.y, self.width, h)
        
        if event.type == pygame.MOUSEMOTION:
            if menu_rect.collidepoint(mx, my):
                rel_y = my - self.y
                self.hovered_idx = int(rel_y // self.item_height)
                if not (0 <= self.hovered_idx < len(self.options)):
                    self.hovered_idx = -1
            else:
                self.hovered_idx = -1
            return menu_rect.collidepoint(mx, my)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if menu_rect.collidepoint(mx, my):
                if event.button == 1:  # Left click
                    if 0 <= self.hovered_idx < len(self.options):
                        # Run callback action
                        action_fn = self.options[self.hovered_idx]["action"]
                        self.hide()
                        action_fn()
                return True
            else:
                # Clicked outside: close menu
                self.hide()
                return False
                
        return False
