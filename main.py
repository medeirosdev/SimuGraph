"""
SimuGraph — Interactive Graph Simulator
Entry point
"""

from __future__ import annotations
import sys
import pygame
import simugraph.settings as cfg
from simugraph.ui.canvas import Canvas
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.camera import Camera


def _load_font(path: str, size: int) -> pygame.font.Font:
    """Try to load the embedded font; fall back to pygame default."""
    try:
        return pygame.font.Font(path, size)
    except FileNotFoundError:
        return pygame.font.SysFont("monospace", size)


def get_next_node_label(graph: Graph) -> str:
    used = {n.label for n in graph.nodes() if n.label}
    for i in range(26):
        label = chr(65 + i)
        if label not in used:
            return label
    suffix = 1
    while True:
        for i in range(26):
            label = f"{chr(65 + i)}{suffix}"
            if label not in used:
                return label
        suffix += 1


def main() -> None:
    pygame.init()
    pygame.display.set_caption(cfg.WINDOW_TITLE)

    screen = pygame.display.set_mode((cfg.WINDOW_W, cfg.WINDOW_H))
    clock = pygame.time.Clock()

    # Sub-surfaces (alpha-capable layers blitted in order each frame)
    canvas = Canvas(cfg.WINDOW_W, cfg.WINDOW_H)
    ui_surf     = pygame.Surface((cfg.WINDOW_W, cfg.WINDOW_H), pygame.SRCALPHA)

    font_ui  = _load_font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
    font_hud = _load_font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_HUD)

    graph  = Graph()
    camera = Camera(cfg.WINDOW_W, cfg.WINDOW_H)

    active_tool = "node"  # "node", "edge", "remove", "select"
    dragging_node: Node | None = None
    snap_enabled = False

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

                # Shortcuts to switch tools
                elif event.key == pygame.K_n:
                    active_tool = "node"
                elif event.key == pygame.K_e:
                    active_tool = "edge"
                elif event.key == pygame.K_r:
                    active_tool = "remove"
                elif event.key == pygame.K_v:
                    active_tool = "select"
                
                # Toggle grid snap: S
                elif event.key == pygame.K_s:
                    snap_enabled = not snap_enabled

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    if my < cfg.WINDOW_H - cfg.HUD_H:
                        wx, wy = camera.screen_to_world(mx, my)
                        
                        # Check if clicked on a node
                        clicked_node = None
                        for node in graph.nodes():
                            dist = ((node.x - wx)**2 + (node.y - wy)**2)**0.5
                            if dist <= node.radius:
                                clicked_node = node
                                break
                        
                        if clicked_node:
                            dragging_node = clicked_node
                            if active_tool == "select":
                                # Deselect others and select this one
                                for node in graph.nodes():
                                    node.selected = False
                                clicked_node.selected = True
                        else:
                            if active_tool == "node":
                                # Avoid placing nodes on top of each other
                                overlap = False
                                for node in graph.nodes():
                                    dist = ((node.x - wx)**2 + (node.y - wy)**2)**0.5
                                    if dist < node.radius * 2:
                                        overlap = True
                                        break
                                if not overlap:
                                    new_node = Node(x=wx, y=wy, label=get_next_node_label(graph))
                                    graph.add_node(new_node)
                            elif active_tool == "select":
                                # Clear selection when clicking empty space
                                for node in graph.nodes():
                                    node.selected = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_node = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_node:
                    mx, my = event.pos
                    wx, wy = camera.screen_to_world(mx, my)
                    if snap_enabled:
                        dragging_node.x = round(wx / cfg.NODE_SNAP_GRID) * cfg.NODE_SNAP_GRID
                        dragging_node.y = round(wy / cfg.NODE_SNAP_GRID) * cfg.NODE_SNAP_GRID
                    else:
                        dragging_node.x = wx
                        dragging_node.y = wy

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
        canvas.draw(camera, graph)
        ui_surf.fill((0, 0, 0, 0))

        # ----------------------------------------------------------------
        # HUD — bottom status bar
        # ----------------------------------------------------------------
        hud_text = (
            f"  Tool: {active_tool.upper()}  |  "
            f"Snap: {'ON' if snap_enabled else 'OFF'}  |  "
            f"Nodes: {graph.node_count()}  |  "
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
        screen.blit(canvas.surface, (0, 0))
        screen.blit(ui_surf, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
