"""
SimuGraph — Interactive Graph Simulator
Entry point
"""

from __future__ import annotations
import sys
import pygame
import simugraph.settings as cfg
from simugraph.ui.canvas import Canvas
from simugraph.ui.sidebar import Sidebar
from simugraph.ui.toolbar import Toolbar
from simugraph.ui.inspector import Inspector
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.camera import Camera
from simugraph.commands.history import (
    CommandHistory, AddNodeCommand, RemoveNodeCommand,
    AddEdgeCommand, RemoveEdgeCommand, MoveNodeCommand
)


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
    drag_start_pos: tuple[float, float] | None = None
    edge_start_node: Node | None = None
    snap_enabled = False
    directed_edges = False
    
    is_panning = False
    
    sidebar = Sidebar()
    toolbar = Toolbar()
    inspector = Inspector()
    history = CommandHistory()

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

                # Undo: Ctrl+Z
                elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                    history.undo(graph)
                
                # Redo: Ctrl+Y
                elif event.key == pygame.K_y and (event.mod & pygame.KMOD_CTRL):
                    history.redo(graph)

                # Theme cycling: Ctrl+T
                elif event.key == pygame.K_t and (event.mod & pygame.KMOD_CTRL):
                    names = list(cfg.THEMES)
                    idx = (names.index(cfg.ACTIVE_THEME_NAME) + 1) % len(names)
                    cfg.set_theme(names[idx])

                # Reset zoom: 0
                elif event.key == pygame.K_0:
                    camera.reset_zoom()

                # Zoom in: PageUp, Keypad Plus, Equals/Plus
                elif event.key in (pygame.K_PAGEUP, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    mx, my = pygame.mouse.get_pos()
                    camera.zoom_at(mx, my, cfg.ZOOM_FACTOR_KEY)

                # Zoom out: PageDown, Keypad Minus, Minus
                elif event.key in (pygame.K_PAGEDOWN, pygame.K_KP_MINUS, pygame.K_MINUS):
                    mx, my = pygame.mouse.get_pos()
                    camera.zoom_at(mx, my, 1.0 / cfg.ZOOM_FACTOR_KEY)

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
                mx, my = event.pos
                
                # Fetch currently selected node
                selected_nodes = [n for n in graph.nodes() if n.selected]
                selected_edges = [e for e in graph.edges() if e.selected]
                sel_node = selected_nodes[0] if selected_nodes else None
                sel_edge = selected_edges[0] if selected_edges else None

                # Check toolbar clicks first
                menu_action = toolbar.handle_click(mx, my)
                if menu_action:
                    menu_id, action_id = menu_action
                    if menu_id == "file":
                        if action_id == "exit":
                            running = False
                        elif action_id == "clear":
                            graph = Graph()
                            history.clear()
                            edge_start_node = None
                    continue
                # If a dropdown is active, clicks outside should close it and consume the event
                if toolbar.active_menu_id:
                    continue

                # Check inspector clicks second
                ins_action = inspector.handle_click(mx, my, sel_node)
                if ins_action:
                    action_type, val = ins_action
                    if action_type == "pin" and sel_node:
                        sel_node.pinned = val
                    elif action_type == "color" and sel_node:
                        sel_node.color = val
                    continue

                # Check sidebar clicks third
                clicked_tool = sidebar.handle_click(mx, my)
                if clicked_tool:
                    active_tool = clicked_tool
                    edge_start_node = None
                    continue

                if event.button == 1:  # Left click
                    # Canvas interaction bounds
                    if cfg.SIDEBAR_W < mx < cfg.WINDOW_W - cfg.INSPECTOR_W and cfg.TOOLBAR_H < my < cfg.WINDOW_H - cfg.HUD_H:
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
                                drag_start_pos = (clicked_node.x, clicked_node.y)
                            elif active_tool == "edge":
                                if edge_start_node is None:
                                    edge_start_node = clicked_node
                                else:
                                    # Create the edge
                                    from simugraph.core.edge import Edge
                                    new_edge = Edge(u=edge_start_node.id, v=clicked_node.id, directed=directed_edges)
                                    history.execute(AddEdgeCommand(new_edge), graph)
                                    edge_start_node = None
                            elif active_tool == "remove":
                                # Remove node and its incident edges (stored for undo)
                                incident_edges = graph.edges_of(clicked_node.id)
                                history.execute(RemoveNodeCommand(clicked_node, incident_edges), graph)
                            else:
                                dragging_node = clicked_node
                                drag_start_pos = (clicked_node.x, clicked_node.y)
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
                                    history.execute(AddNodeCommand(new_node), graph)
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
                                            to_remove = edge
                                            break
                                if to_remove:
                                    history.execute(RemoveEdgeCommand(to_remove), graph)

                elif event.button == 2:  # Middle click starts panning
                    if cfg.SIDEBAR_W < mx < cfg.WINDOW_W - cfg.INSPECTOR_W and cfg.TOOLBAR_H < my < cfg.WINDOW_H - cfg.HUD_H:
                        is_panning = True

                elif event.button == 3:  # Right click deletes nodes / edges in any tool
                    if cfg.SIDEBAR_W < mx < cfg.WINDOW_W - cfg.INSPECTOR_W and cfg.TOOLBAR_H < my < cfg.WINDOW_H - cfg.HUD_H:
                        wx, wy = camera.screen_to_world(mx, my)
                        
                        # Find clicked node
                        clicked_node = None
                        for node in graph.nodes():
                            dist = ((node.x - wx)**2 + (node.y - wy)**2)**0.5
                            if dist <= node.radius:
                                clicked_node = node
                                break
                        
                        if clicked_node:
                            incident_edges = graph.edges_of(clicked_node.id)
                            history.execute(RemoveNodeCommand(clicked_node, incident_edges), graph)
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
                                        to_remove = edge
                                        break
                            if to_remove:
                                history.execute(RemoveEdgeCommand(to_remove), graph)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if dragging_node and drag_start_pos:
                        # If node has moved, register the MoveNodeCommand in history
                        end_pos = (dragging_node.x, dragging_node.y)
                        if end_pos != drag_start_pos:
                            history.push(MoveNodeCommand(dragging_node.id, drag_start_pos, end_pos))
                    dragging_node = None
                    drag_start_pos = None
                elif event.button == 2:  # Middle click release stops panning
                    is_panning = False

            elif event.type == pygame.MOUSEMOTION:
                if is_panning:
                    camera.pan(event.rel[0], event.rel[1])
                elif dragging_node:
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
        
        # Draw Sidebar
        sidebar.draw(ui_surf, active_tool)
        
        # Draw Toolbar
        toolbar.draw(ui_surf)

        # Draw Inspector
        selected_nodes = [n for n in graph.nodes() if n.selected]
        selected_edges = [e for e in graph.edges() if e.selected]
        sel_node = selected_nodes[0] if selected_nodes else None
        sel_edge = selected_edges[0] if selected_edges else None
        inspector.draw(ui_surf, sel_node, sel_edge)

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
