"""
Keyboard shortcuts cheatsheet overlay component.
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg


class CheatsheetOverlay:
    """
    Centered modal overlay showing keyboard shortcuts cheatsheet.
    Closes on any key press or click.
    """

    def __init__(self) -> None:
        self.width = 540
        self.height = 420
        self.rect = pygame.Rect(
            (cfg.WINDOW_W - self.width) // 2,
            (cfg.WINDOW_H - self.height) // 2,
            self.width,
            self.height
        )

        try:
            self.font_title = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_HUD + 2)
            self.font_body = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font_title = pygame.font.SysFont("monospace", cfg.FONT_SIZE_HUD + 2)
            self.font_body = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)

        # Cheatsheet items: (Shortcut, Action description)
        self.shortcuts = [
            ("Esc", "Exit / Cancel"),
            ("Ctrl + T", "Cycle Theme"),
            ("Ctrl + Z", "Undo Action"),
            ("Ctrl + Y", "Redo Action"),
            ("N", "Node Tool"),
            ("E", "Edge Tool"),
            ("R", "Remove Tool"),
            ("V", "Select / Move Tool"),
            ("S", "Toggle Grid Snap"),
            ("D", "Toggle Directed Edge"),
            ("0 (zero)", "Reset View Zoom"),
            ("+ / PageUp", "Zoom In"),
            ("- / PageDown", "Zoom Out"),
            ("? / /", "Toggle Cheatsheet"),
        ]

    def draw(self, surface: pygame.Surface) -> None:
        # 1. Dim background
        dim_surf = pygame.Surface((cfg.WINDOW_W, cfg.WINDOW_H), pygame.SRCALPHA)
        dim_surf.fill((10, 10, 15, 180))
        surface.blit(dim_surf, (0, 0))

        # 2. Draw panel background
        pygame.draw.rect(surface, cfg.THEME["sidebar_bg"], self.rect, border_radius=10)
        pygame.draw.rect(surface, cfg.THEME["panel_border"], self.rect, width=2, border_radius=10)

        # 3. Draw Title
        title_surf = self.font_title.render("KEYBOARD SHORTCUTS & CONTROLS", True, cfg.THEME["accent"])
        title_x = self.rect.x + (self.width - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, self.rect.y + 25))
        pygame.draw.line(
            surface,
            cfg.THEME["panel_border"],
            (self.rect.x + 30, self.rect.y + 55),
            (self.rect.x + self.width - 30, self.rect.y + 55),
            1
        )

        # 4. Draw shortcuts list in two columns
        col_w = (self.width - 80) // 2
        row_h = 24
        start_y = self.rect.y + 75

        for idx, (keys, desc) in enumerate(self.shortcuts):
            col = idx % 2
            row = idx // 2
            
            x = self.rect.x + 40 + col * (col_w + 20)
            y = start_y + row * row_h

            # Render key shortcut in accent highlight color
            key_surf = self.font_body.render(keys.ljust(13), True, cfg.THEME["accent"])
            desc_surf = self.font_body.render(desc, True, cfg.THEME["text"])
            
            surface.blit(key_surf, (x, y))
            surface.blit(desc_surf, (x + key_surf.get_width() + 5, y))

        # 5. Draw dismiss notice at the bottom
        notice_surf = self.font_body.render("Press any key or click to dismiss", True, cfg.THEME["text_dim"])
        notice_x = self.rect.x + (self.width - notice_surf.get_width()) // 2
        surface.blit(notice_surf, (notice_x, self.rect.y + self.height - 35))
