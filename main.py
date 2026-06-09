"""
SimuGraph — Interactive Graph Simulator
Entry point
"""

from __future__ import annotations
import sys
import pygame
import simugraph.settings as cfg
from simugraph.core.graph import Graph
from simugraph.camera import Camera


def _load_font(path: str, size: int) -> pygame.font.Font:
    """Try to load the embedded font; fall back to pygame default."""
    try:
        return pygame.font.Font(path, size)
    except FileNotFoundError:
        return pygame.font.SysFont("monospace", size)


def main() -> None:
    pygame.init()
    pygame.display.set_caption(cfg.WINDOW_TITLE)

    screen = pygame.display.set_mode((cfg.WINDOW_W, cfg.WINDOW_H))
    clock = pygame.time.Clock()

    # Sub-surfaces (alpha-capable layers blitted in order each frame)
    canvas_surf = pygame.Surface((cfg.WINDOW_W, cfg.WINDOW_H), pygame.SRCALPHA)
    ui_surf     = pygame.Surface((cfg.WINDOW_W, cfg.WINDOW_H), pygame.SRCALPHA)

    font_ui  = _load_font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
    font_hud = _load_font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_HUD)

    graph  = Graph()
    camera = Camera(cfg.WINDOW_W, cfg.WINDOW_H)

    running = True
    while running:
        dt = clock.tick(cfg.FPS)

        # ----------------------------------------------------------------
        # Event loop
        # ----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Theme cycling: Ctrl+T
                elif event.key == pygame.K_t and (event.mod & pygame.KMOD_CTRL):
                    names = list(cfg.THEMES)
                    idx = (names.index(cfg.ACTIVE_THEME_NAME) + 1) % len(names)
                    cfg.set_theme(names[idx])

                # Reset zoom: 0
                elif event.key == pygame.K_0:
                    camera.reset_zoom()

            # Scroll-wheel zoom centred on mouse
            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                factor = cfg.ZOOM_FACTOR_SCROLL if event.y > 0 else 1 / cfg.ZOOM_FACTOR_SCROLL
                camera.zoom_at(mx, my, factor)

        # ----------------------------------------------------------------
        # Clear layers
        # ----------------------------------------------------------------
        bg = cfg.THEME["bg"]
        screen.fill(bg)
        canvas_surf.fill((0, 0, 0, 0))
        ui_surf.fill((0, 0, 0, 0))

        # ----------------------------------------------------------------
        # HUD — bottom status bar
        # ----------------------------------------------------------------
        hud_text = (
            f"  Nodes: {graph.node_count()}  |  "
            f"Edges: {graph.edge_count()}  |  "
            f"Zoom: {camera.zoom_percent()}%  |  "
            f"Theme: {cfg.ACTIVE_THEME_NAME}  |  "
            f"FPS: {clock.get_fps():.0f}"
        )
        hud_color = cfg.THEME["hud_bg"]
        hud_rect = pygame.Rect(0, cfg.WINDOW_H - cfg.HUD_H, cfg.WINDOW_W, cfg.HUD_H)
        hud_surf = pygame.Surface((cfg.WINDOW_W, cfg.HUD_H), pygame.SRCALPHA)
        hud_surf.fill(hud_color)
        label = font_hud.render(hud_text, True, cfg.THEME["text_dim"])
        hud_surf.blit(label, (8, (cfg.HUD_H - label.get_height()) // 2))
        ui_surf.blit(hud_surf, (0, cfg.WINDOW_H - cfg.HUD_H))

        # ----------------------------------------------------------------
        # Compose and flip
        # ----------------------------------------------------------------
        screen.blit(canvas_surf, (0, 0))
        screen.blit(ui_surf, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
