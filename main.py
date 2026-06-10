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
from simugraph.ui.hud import HUD
from simugraph.ui.dialog import InputDialog
from simugraph.ui.overlay import CheatsheetOverlay
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.camera import Camera
from simugraph.commands.history import (
    CommandHistory, AddNodeCommand, RemoveNodeCommand,
    AddEdgeCommand, RemoveEdgeCommand, MoveNodeCommand,
    RenameNodeCommand, ChangeNodeColorCommand, ToggleNodePinCommand,
    ColorComponentsCommand, ChangeNodeWeightCommand, ChangeEdgeWeightCommand,
    MoveNodesCommand
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
    hud = HUD()
    history = CommandHistory()
    
    # Dialog management
    active_dialog: InputDialog | None = None
    dialog_callback = None
    
    # Cheatsheet overlay
    cheatsheet = CheatsheetOverlay()
    show_cheatsheet = False
    
    # Double-click detection
    last_click_time = 0
    last_clicked_node_id: str | None = None

    # Multi-node box selection
    selection_box_start: tuple[int, int] | None = None
    selection_box_current: tuple[int, int] | None = None

    # Connectivity highlights (Bridges & Articulation Points)
    articulation_points: set[str] = set()
    bridges: set[str] = set()

    def clear_highlights():
        articulation_points.clear()
        bridges.clear()
    history.on_change_callbacks.append(clear_highlights)

    # Spring Layout state
    layout_steps_remaining = 0
    layout_initial_positions = {}
    layout_temperature = 20.0

    def stop_layout():
        nonlocal layout_steps_remaining
        layout_steps_remaining = 0
    history.on_change_callbacks.append(stop_layout)

    # Node hover tooltip state
    hovered_node_id: str | None = None
    hover_start_ticks = 0
    tooltip_font = _load_font(cfg.FONT_MONO_PATH, 11)

    dragging_group: dict[str, tuple[float, float]] = {}

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

            # Dismiss cheatsheet on any key or click
            if show_cheatsheet:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    show_cheatsheet = False
                continue

            # Route events to active modal dialog if open
            if active_dialog is not None:
                done, res = active_dialog.handle_event(event)
                if done:
                    if res is not None and dialog_callback is not None:
                        dialog_callback(res)
                    active_dialog = None
                    dialog_callback = None
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

                # Auto-layout: L
                elif event.key == pygame.K_l:
                    if layout_steps_remaining == 0:
                        nodes_list = graph.nodes()
                        if len(nodes_list) >= 2:
                            layout_initial_positions = {n.id: (n.x, n.y) for n in nodes_list}
                            layout_steps_remaining = 75
                            layout_temperature = 25.0

                # Toggle cheatsheet: ? / /
                elif event.key in (pygame.K_SLASH, pygame.K_QUESTION) or (event.key == pygame.K_SLASH and (event.mod & pygame.KMOD_SHIFT)):
                    show_cheatsheet = True

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
                    elif menu_id == "algo":
                        if action_id == "scc":
                            from simugraph.algorithms.scc import find_sccs
                            sccs = find_sccs(graph)
                            color_map = {}
                            for comp_idx, comp in enumerate(sccs):
                                color = cfg.SCC_PALETTE[comp_idx % len(cfg.SCC_PALETTE)]
                                for nid in comp:
                                    color_map[nid] = color
                            history.execute(ColorComponentsCommand(color_map), graph)
                        elif action_id == "bridges":
                            from simugraph.algorithms.connectivity import find_bridges_and_articulation_points
                            ap_ids, br_ids = find_bridges_and_articulation_points(graph)
                            articulation_points.clear()
                            articulation_points.update(ap_ids)
                            bridges.clear()
                            bridges.update(br_ids)
                    continue
                # If a dropdown is active, clicks outside should close it and consume the event
                if toolbar.active_menu_id:
                    continue

                # Check inspector clicks second
                ins_action = inspector.handle_click(mx, my, sel_node, sel_edge)
                if ins_action:
                    action_type, val = ins_action
                    if action_type == "pin" and sel_node:
                        history.execute(ToggleNodePinCommand(sel_node.id, sel_node.pinned, val), graph)
                    elif action_type == "color" and sel_node:
                        history.execute(ChangeNodeColorCommand(sel_node.id, sel_node.color, val), graph)
                    elif action_type == "node_weight" and sel_node:
                        active_dialog = InputDialog("Node Weight", initial_value=str(sel_node.weight), placeholder="Weight (number)")
                        def make_node_weight_cb(node_to_edit):
                            return lambda val_str: history.execute(
                                ChangeNodeWeightCommand(node_to_edit.id, node_to_edit.weight, float(val_str) if val_str else 0.0),
                                graph
                            )
                        dialog_callback = make_node_weight_cb(sel_node)
                    elif action_type == "edge_weight" and sel_edge:
                        active_dialog = InputDialog("Edge Weight", initial_value=str(sel_edge.weight), placeholder="Weight (number)")
                        def make_edge_weight_cb(edge_to_edit):
                            return lambda val_str: history.execute(
                                ChangeEdgeWeightCommand(edge_to_edit.id, edge_to_edit.weight, float(val_str) if val_str else 1.0),
                                graph
                            )
                        dialog_callback = make_edge_weight_cb(sel_edge)
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
                            # Double-click rename detection
                            now = pygame.time.get_ticks()
                            if now - last_click_time < 300 and clicked_node.id == last_clicked_node_id:
                                # Start rename dialog
                                active_dialog = InputDialog("Rename Node", initial_value=clicked_node.label, placeholder="New Label")
                                def make_rename_cb(node_to_rename):
                                    return lambda val: history.execute(RenameNodeCommand(node_to_rename.id, node_to_rename.label, val), graph)
                                dialog_callback = make_rename_cb(clicked_node)
                                dragging_node = None
                                last_clicked_node_id = None
                                last_click_time = 0
                                continue
                            
                            last_click_time = now
                            last_clicked_node_id = clicked_node.id

                            if active_tool == "select":
                                if not clicked_node.selected:
                                    # Deselect others and select this one
                                    for node in graph.nodes():
                                        node.selected = False
                                    clicked_node.selected = True
                                dragging_group = {node.id: (node.x, node.y) for node in graph.nodes() if node.selected}
                                dragging_node = clicked_node
                                drag_start_pos = (clicked_node.x, clicked_node.y)
                            elif active_tool == "edge":
                                if edge_start_node is None:
                                    edge_start_node = clicked_node
                                else:
                                    # Open modal for edge weight
                                    active_dialog = InputDialog("Edge Weight", initial_value="1.0", placeholder="Weight (number)")
                                    
                                    def make_edge_cb(u_node, v_node, dir_flag):
                                        def cb(val_str):
                                            try:
                                                weight_val = float(val_str)
                                            except ValueError:
                                                weight_val = 1.0
                                            from simugraph.core.edge import Edge
                                            new_edge = Edge(u=u_node.id, v=v_node.id, weight=weight_val, directed=dir_flag)
                                            history.execute(AddEdgeCommand(new_edge), graph)
                                        return cb

                                    dialog_callback = make_edge_cb(edge_start_node, clicked_node, directed_edges)
                                    edge_start_node = None
                            elif active_tool == "remove":
                                # Remove node and its incident edges (stored for undo)
                                incident_edges = graph.edges_of(clicked_node.id)
                                history.execute(RemoveNodeCommand(clicked_node, incident_edges), graph)
                            else:
                                if clicked_node.selected:
                                    dragging_group = {node.id: (node.x, node.y) for node in graph.nodes() if node.selected}
                                else:
                                    dragging_group = {clicked_node.id: (clicked_node.x, clicked_node.y)}
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
                                # Clear selection when clicking empty space and start box selection
                                for node in graph.nodes():
                                    node.selected = False
                                selection_box_start = (mx, my)
                                selection_box_current = (mx, my)
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
                    selection_box_start = None
                    selection_box_current = None
                    if dragging_node and drag_start_pos:
                        if len(dragging_group) > 1:
                            moves = {}
                            for nid, start_pos in dragging_group.items():
                                n = graph.get_node(nid)
                                if n:
                                    end_pos = (n.x, n.y)
                                    if start_pos != end_pos:
                                        moves[nid] = (start_pos, end_pos)
                            if moves:
                                history.push(MoveNodesCommand(moves))
                        else:
                            end_pos = (dragging_node.x, dragging_node.y)
                            if end_pos != drag_start_pos:
                                history.push(MoveNodeCommand(dragging_node.id, drag_start_pos, end_pos))
                    dragging_node = None
                    drag_start_pos = None
                    dragging_group.clear()
                elif event.button == 2:  # Middle click release stops panning
                    is_panning = False

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if is_panning:
                    camera.pan(event.rel[0], event.rel[1])
                elif selection_box_start is not None:
                    selection_box_current = (mx, my)
                    wx_start, wy_start = camera.screen_to_world(*selection_box_start)
                    wx_curr, wy_curr = camera.screen_to_world(*selection_box_current)
                    x_min, x_max = sorted([wx_start, wx_curr])
                    y_min, y_max = sorted([wy_start, wy_curr])
                    for node in graph.nodes():
                        node.selected = (x_min <= node.x <= x_max and y_min <= node.y <= y_max)
                elif dragging_node and drag_start_pos:
                    wx, wy = camera.screen_to_world(mx, my)
                    dx = wx - drag_start_pos[0]
                    dy = wy - drag_start_pos[1]
                    for nid, start_pos in dragging_group.items():
                        node = graph.get_node(nid)
                        if node:
                            if snap_enabled:
                                node.x = round((start_pos[0] + dx) / cfg.NODE_SNAP_GRID) * cfg.NODE_SNAP_GRID
                                node.y = round((start_pos[1] + dy) / cfg.NODE_SNAP_GRID) * cfg.NODE_SNAP_GRID
                            else:
                                node.x = start_pos[0] + dx
                                node.y = start_pos[1] + dy

            # Scroll-wheel zoom centred on mouse
            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                factor = cfg.ZOOM_FACTOR_SCROLL if event.y > 0 else 1 / cfg.ZOOM_FACTOR_SCROLL
                camera.zoom_at(mx, my, factor)

        # --- Update spring layout ---
        if layout_steps_remaining > 0:
            from simugraph.algorithms.layout import run_fruchterman_reingold_step
            run_fruchterman_reingold_step(graph, temp=layout_temperature)
            layout_temperature = max(1.0, layout_temperature * 0.94)
            layout_steps_remaining -= 1
            if layout_steps_remaining == 0:
                # Final register of MoveNodesCommand to support undo/redo
                moves = {}
                for node in graph.nodes():
                    old_pos = layout_initial_positions.get(node.id)
                    if old_pos:
                        new_pos = (node.x, node.y)
                        if old_pos != new_pos:
                            moves[node.id] = (old_pos, new_pos)
                if moves:
                    history.push(MoveNodesCommand(moves))

        # Track node hover for tooltip
        mx, my = pygame.mouse.get_pos()
        m_wx, m_wy = camera.screen_to_world(mx, my)
        current_hovered = None
        if cfg.SIDEBAR_W < mx < cfg.WINDOW_W - cfg.INSPECTOR_W and cfg.TOOLBAR_H < my < cfg.WINDOW_H - cfg.HUD_H:
            for node in graph.nodes():
                dist = ((node.x - m_wx)**2 + (node.y - m_wy)**2)**0.5
                if dist <= node.radius:
                    current_hovered = node
                    break
        
        if current_hovered:
            if hovered_node_id != current_hovered.id:
                hovered_node_id = current_hovered.id
                hover_start_ticks = pygame.time.get_ticks()
        else:
            hovered_node_id = None
            hover_start_ticks = 0

        # ----------------------------------------------------------------
        # Clear layers
        # ----------------------------------------------------------------
        bg = cfg.THEME["bg"]
        screen.fill(bg)
        
        sel_box = None
        if selection_box_start and selection_box_current:
            sel_box = (*selection_box_start, *selection_box_current)
        canvas.draw(camera, graph, edge_start_node, sel_box, articulation_points, bridges)
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
        
        # Draw HUD status bar
        hud.draw(ui_surf, active_tool, snap_enabled, directed_edges, graph, camera, clock.get_fps())
        
        # Draw Cheatsheet Overlay
        if show_cheatsheet:
            cheatsheet.draw(ui_surf)
        
        # Draw Modal Dialogs
        if active_dialog is not None:
            active_dialog.draw(ui_surf)

        # Draw node hover tooltip (with 300ms delay)
        if hovered_node_id and pygame.time.get_ticks() - hover_start_ticks >= 300:
            h_node = graph.get_node(hovered_node_id)
            if h_node:
                # Calculate degree and degree centrality
                deg = graph.degree(h_node.id)
                n_count = graph.node_count()
                centrality = deg / max(1, n_count - 1)
                
                # Render text lines
                lines = [
                    f"Label: {h_node.label}",
                    f"Degree: {deg}",
                    f"Centrality: {centrality:.2f}"
                ]
                
                rendered_lines = [tooltip_font.render(ln, True, (240, 240, 250)) for ln in lines]
                w = max(surf.get_width() for surf in rendered_lines) + 16
                h = sum(surf.get_height() for surf in rendered_lines) + 12
                
                # Position near mouse, clamped inside canvas bounds
                tx = mx + 15
                ty = my + 15
                
                canvas_r = cfg.WINDOW_W - cfg.INSPECTOR_W
                canvas_b = cfg.WINDOW_H - cfg.HUD_H
                
                if tx + w > canvas_r:
                    tx = mx - w - 10
                if ty + h > canvas_b:
                    ty = my - h - 10
                
                # Background rect
                bg_rect = pygame.Rect(tx, ty, w, h)
                # Drawing transparent surface for background
                tip_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                tip_surf.fill((25, 25, 35, 230))  # dark slate with 90% opacity
                pygame.draw.rect(tip_surf, cfg.THEME["panel_border"], (0, 0, w, h), width=1, border_radius=4)
                
                # Blit text onto tip surface
                curr_y = 6
                for r_line in rendered_lines:
                    tip_surf.blit(r_line, (8, curr_y))
                    curr_y += r_line.get_height() + 2
                
                ui_surf.blit(tip_surf, (tx, ty))

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
