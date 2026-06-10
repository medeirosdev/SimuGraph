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


class MultiInputDialog:
    """
    Centered modal dialog that captures multiple text inputs.
    Used for graph generator parameters.
    """

    def __init__(self, title: str, fields: list[tuple[str, str]]) -> None:
        self.title = title
        # fields is a list of [label, value]
        self.fields = [[f[0], f[1]] for f in fields]
        self.active_idx = 0
        
        # Dimensions
        self.width = 380
        self.height = 100 + len(fields) * 48
        self.rect = pygame.Rect(
            (cfg.WINDOW_W - self.width) // 2,
            (cfg.WINDOW_H - self.height) // 2,
            self.width,
            self.height
        )
        
        self.input_rects = []
        for idx in range(len(fields)):
            rect = pygame.Rect(
                self.rect.x + 160,
                self.rect.y + 60 + idx * 42,
                190,
                30
            )
            self.input_rects.append(rect)
            
        self.ok_rect = pygame.Rect(self.rect.x + self.width - 120, self.rect.y + self.height - 45, 100, 30)
        self.cancel_rect = pygame.Rect(self.rect.x + 20, self.rect.y + self.height - 45, 100, 30)

        try:
            self.font_title = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
            self.font_text = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font_title = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)
            self.font_text = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)

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

        # Draw Fields
        for idx, (label, val) in enumerate(self.fields):
            # Label
            lbl_surf = self.font_text.render(label, True, cfg.THEME["text"])
            lbl_y = self.input_rects[idx].y + (self.input_rects[idx].height - lbl_surf.get_height()) // 2
            surface.blit(lbl_surf, (self.rect.x + 20, lbl_y))
            
            # Input Box
            pygame.draw.rect(surface, cfg.THEME["toolbar_bg"], self.input_rects[idx], border_radius=4)
            
            # Highlight active field border
            border_color = cfg.THEME["accent"] if idx == self.active_idx else cfg.THEME["panel_border"]
            border_w = 2 if idx == self.active_idx else 1
            pygame.draw.rect(surface, border_color, self.input_rects[idx], width=border_w, border_radius=4)
            
            # Render typed value
            val_surf = self.font_text.render(val, True, cfg.THEME["text"])
            surface.blit(val_surf, (self.input_rects[idx].x + 8, self.input_rects[idx].y + (self.input_rects[idx].height - val_surf.get_height()) // 2))

            # Draw cursor blinking in active field
            if idx == self.active_idx and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = self.input_rects[idx].x + 8 + self.font_text.size(val)[0]
                pygame.draw.line(surface, cfg.THEME["accent"], (cursor_x, self.input_rects[idx].y + 6), (cursor_x, self.input_rects[idx].y + self.input_rects[idx].height - 6), 2)

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

    def handle_event(self, event: pygame.event.Event) -> tuple[bool, list[str] | None]:
        """
        Processes events for the multi-field modal dialog.
        Returns (is_finished, result_list)
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True, [f[1] for f in self.fields]
            elif event.key == pygame.K_ESCAPE:
                return True, None
            elif event.key == pygame.K_TAB:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.active_idx = (self.active_idx - 1) % len(self.fields)
                else:
                    self.active_idx = (self.active_idx + 1) % len(self.fields)
            elif event.key == pygame.K_BACKSPACE:
                self.fields[self.active_idx][1] = self.fields[self.active_idx][1][:-1]
            else:
                # Capture text input
                if event.unicode and event.unicode.isprintable():
                    if len(self.fields[self.active_idx][1]) < 12:
                        self.fields[self.active_idx][1] += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                if self.ok_rect.collidepoint(mx, my):
                    return True, [f[1] for f in self.fields]
                elif self.cancel_rect.collidepoint(mx, my) or not self.rect.collidepoint(mx, my):
                    return True, None
                
                # Check if clicked on any field box
                for idx, r in enumerate(self.input_rects):
                    if r.collidepoint(mx, my):
                        self.active_idx = idx
                        break

        return False, None
