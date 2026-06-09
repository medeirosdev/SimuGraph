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


def distance_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    """Distance from point P to segment AB in world space."""
    l2 = (ax - bx)**2 + (ay - by)**2
    if l2 == 0:
        return ((px - ax)**2 + (py - ay)**2)**0.5
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2
    t = max(0.0, min(1.0, t))
    proj_x = ax + t * (bx - ax)
    proj_y = ay + t * (by - ay)
    return ((px - proj_x)**2 + (py - proj_y)**2)**0.5


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
    edge_start_node: Node | None = None
    snap_enabled = False
    directed_edges = False

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
                    # Cancel edge creation first, otherwise exit
                    if edge_start_node:
                        edge_start_node = None
                    else:
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
                    edge_start_node = None
                elif event.key == pygame.K_e:
                    active_tool = "edge"
                    edge_start_node = None
                elif event.key == pygame.K_r:
                    active_tool = "remove"
                    edge_start_node = None
                elif event.key == pygame.K_v:
                    active_tool = "select"
                    edge_start_node = None
                
                # Toggle grid snap: S
                elif event.key == pygame.K_s:
                    snap_enabled = not snap_enabled
                
                # Toggle directed edges: D
                elif event.key == pygame.K_d:
                    directed_edges = not directed_edges

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
                            if active_tool == "select":
                                # Deselect others and select this one
                                for node in graph.nodes():
                                    node.selected = False
                                clicked_node.selected = True
                                dragging_node = clicked_node
                            elif active_tool == "edge":
                                if edge_start_node is None:
                                    edge_start_node = clicked_node
                                else:
                                    # Create the edge
                                    from simugraph.core.edge import Edge
                                    new_edge = Edge(u=edge_start_node.id, v=clicked_node.id, directed=directed_edges)
                                    graph.add_edge(new_edge)
                                    edge_start_node = None
                            elif active_tool == "remove":
                                graph.remove_node(clicked_node.id)
                            else:
                                dragging_node = clicked_node
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
                            # Clicking empty space cancels edge start
                            elif active_tool == "edge":
                                edge_start_node = None
                            elif active_tool == "remove":
                                # Check if clicked on an edge
                                threshold = 8.0 / camera.zoom
                                to_remove = None
                                for edge in graph.edges():
                                    u = graph.get_node(edge.u)
                                    v = graph.get_node(edge.v)
                                    if u and v:
                                        d = distance_to_segment(wx, wy, u.x, u.y, v.x, v.y)
                                        if d <= threshold:
                                            to_remove = edge.id
                                            break
                                if to_remove:
                                    graph.remove_edge(to_remove)

                elif event.button == 3:  # Right click deletes nodes / edges in any tool
                    mx, my = event.pos
                    if my < cfg.WINDOW_H - cfg.HUD_H:
                        wx, wy = camera.screen_to_world(mx, my)
                        
                        # Find clicked node
                        clicked_node = None
                        for node in graph.nodes():
                            dist = ((node.x - wx)**2 + (node.y - wy)**2)**0.5
                            if dist <= node.radius:
                                clicked_node = node
                                break
                        
                        if clicked_node:
                            graph.remove_node(clicked_node.id)
                            if edge_start_node == clicked_node:
                                edge_start_node = None
                        else:
                            # Try to find clicked edge
                            threshold = 8.0 / camera.zoom
                            to_remove = None
                            for edge in graph.edges():
                                u = graph.get_node(edge.u)
                                v = graph.get_node(edge.v)
                                if u and v:
                                    d = distance_to_segment(wx, wy, u.x, u.y, v.x, v.y)
                                    if d <= threshold:
                                        to_remove = edge.id
                                        break
                            if to_remove:
                                graph.remove_edge(to_remove)

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
        canvas.draw(camera, graph, edge_start_node)
        ui_surf.fill((0, 0, 0, 0))

        # ----------------------------------------------------------------
        # HUD — bottom status bar
        # ----------------------------------------------------------------
        hud_text = (
            f"  Tool: {active_tool.upper()}  |  "
            f"Snap: {'ON' if snap_enabled else 'OFF'}  |  "
            f"Dir: {'ON' if directed_edges else 'OFF'}  |  "
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
