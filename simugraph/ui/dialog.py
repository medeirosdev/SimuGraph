"""
Modal Dialog components for user input (renaming nodes, changing edge weights).
"""

from __future__ import annotations
import pygame
import simugraph.settings as cfg


class InputDialog:
    """
    Centered modal dialog that captures text input.
    Can be used for renaming nodes or setting edge weights.
    """

    def __init__(self, title: str, initial_value: str = "", placeholder: str = "") -> None:
        self.title = title
        self.value = initial_value
        self.placeholder = placeholder
        
        # Dimensions
        self.width = 320
        self.height = 160
        self.rect = pygame.Rect(
            (cfg.WINDOW_W - self.width) // 2,
            (cfg.WINDOW_H - self.height) // 2,
            self.width,
            self.height
        )
        self.input_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 60, self.width - 40, 32)
        self.ok_rect = pygame.Rect(self.rect.x + self.width - 120, self.rect.y + 110, 100, 30)
        self.cancel_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 110, 100, 30)

        # Cache font
        try:
            self.font_title = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
            self.font_input = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font_title = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)
            self.font_input = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)

    def draw(self, surface: pygame.Surface) -> None:
        # Dim background
        dim_surf = pygame.Surface((cfg.WINDOW_W, cfg.WINDOW_H), pygame.SRCALPHA)
        dim_surf.fill((10, 10, 15, 160))
        surface.blit(dim_surf, (0, 0))

        # Draw dialog box background
        pygame.draw.rect(surface, cfg.THEME["sidebar_bg"], self.rect, border_radius=8)
        pygame.draw.rect(surface, cfg.THEME["panel_border"], self.rect, width=2, border_radius=8)

        # Draw Title
        title_surf = self.font_title.render(self.title, True, cfg.THEME["accent"])
        surface.blit(title_surf, (self.rect.x + 20, self.rect.y + 20))

        # Draw Text Input Box
        pygame.draw.rect(surface, cfg.THEME["toolbar_bg"], self.input_rect, border_radius=4)
        pygame.draw.rect(surface, cfg.THEME["accent"], self.input_rect, width=1, border_radius=4)

        # Render typed value or placeholder
        if self.value:
            text_color = cfg.THEME["text"]
            disp_text = self.value
        else:
            text_color = cfg.THEME["text_dim"]
            disp_text = self.placeholder

        txt_surf = self.font_input.render(disp_text, True, text_color)
        surface.blit(txt_surf, (self.input_rect.x + 10, self.input_rect.y + (self.input_rect.height - txt_surf.get_height()) // 2))

        # Draw cursor blinking (optional, let's draw a simple bar at the end)
        if self.value and (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = self.input_rect.x + 10 + self.font_input.size(self.value)[0]
            pygame.draw.line(surface, cfg.THEME["accent"], (cursor_x, self.input_rect.y + 6), (cursor_x, self.input_rect.y + self.input_rect.height - 6), 2)

        # Draw buttons (OK, Cancel)
        mx, my = pygame.mouse.get_pos()
        
        # OK Button
        ok_hover = self.ok_rect.collidepoint(mx, my)
        ok_bg = cfg.THEME["accent"] if ok_hover else cfg.THEME["panel_border"]
        pygame.draw.rect(surface, ok_bg, self.ok_rect, border_radius=4)
        ok_lbl = self.font_title.render("OK", True, cfg.THEME["sidebar_bg"] if ok_hover else cfg.THEME["text"])
        surface.blit(ok_lbl, ok_lbl.get_rect(center=self.ok_rect.center))

        # Cancel Button
        cancel_hover = self.cancel_rect.collidepoint(mx, my)
        cancel_bg = cfg.THEME["context_bg"] if cancel_hover else cfg.THEME["sidebar_bg"]
        pygame.draw.rect(surface, cancel_bg, self.cancel_rect, border_radius=4)
        pygame.draw.rect(surface, cfg.THEME["panel_border"], self.cancel_rect, width=1, border_radius=4)
        cancel_lbl = self.font_title.render("Cancel", True, cfg.THEME["text"])
        surface.blit(cancel_lbl, cancel_lbl.get_rect(center=self.cancel_rect.center))

    def handle_event(self, event: pygame.event.Event) -> tuple[bool, str | None]:
        """
        Processes events for the modal dialog.
        Returns (is_finished, result)
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True, self.value
            elif event.key == pygame.K_ESCAPE:
                return True, None
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            else:
                # Capture text input
                if event.unicode and event.unicode.isprintable():
                    # Limit label size to 12 chars
                    if len(self.value) < 12:
                        self.value += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                if self.ok_rect.collidepoint(mx, my):
                    return True, self.value
                elif self.cancel_rect.collidepoint(mx, my) or not self.rect.collidepoint(mx, my):
                    return True, None

        return False, None
