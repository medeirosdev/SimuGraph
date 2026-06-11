from __future__ import annotations
import pygame
import simugraph.settings as cfg
from simugraph.core.properties import GraphProperties
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class PropertiesPanel:
    def __init__(self, inspector_x: int, inspector_y: int, inspector_w: int) -> None:
        self.x = inspector_x
        self.y = inspector_y
        self.width = inspector_w
        self.heatmap_rects: dict[str, pygame.Rect] = {}
        
        self.reload_fonts()

    def reload_fonts(self) -> None:
        try:
            self.font_body = pygame.font.Font(cfg.FONT_MONO_PATH, cfg.FONT_SIZE_UI)
        except FileNotFoundError:
            self.font_body = pygame.font.SysFont("monospace", cfg.FONT_SIZE_UI)

    def draw(self, surface: pygame.Surface, graph: Graph, centrality_mode: str | None) -> None:
        self.heatmap_rects.clear()
        
        y_offset = self.y + 60
        text_color = cfg.THEME["text"]
        accent_color = cfg.THEME["accent"]

        props = GraphProperties(graph)

        # Title
        title_lbl = self.font_body.render("Graph Statistics", True, accent_color)
        surface.blit(title_lbl, (self.x + 15, y_offset))
        y_offset += 30

        # Node/Edge count
        nodes_cnt = len(list(graph.nodes()))
        edges_cnt = len(list(graph.edges()))
        stats_lbl = self.font_body.render(f"Nodes: {nodes_cnt}   Edges: {edges_cnt}", True, text_color)
        surface.blit(stats_lbl, (self.x + 15, y_offset))
        y_offset += 25

        # Properties
        is_conn = props.is_connected()
        is_bip, _ = props.is_bipartite()
        has_cyc = props.has_cycle()
        is_tree = props.is_tree()
        chrom = props.chromatic_number()
        dia = props.diameter()

        conn_str = f"Connected: {'YES' if is_conn else 'NO'}"
        bip_str = f"Bipartite: {'YES' if is_bip else 'NO'}"
        cyc_str = f"Has Cycle: {'YES' if has_cyc else 'NO'}"
        tree_str = f"Is Tree:   {'YES' if is_tree else 'NO'}"
        chrom_str = f"Chromatic #: {chrom}"
        dia_str = f"Diameter:  {dia:.1f}" if dia != float('inf') else "Diameter:  inf"

        for s in [conn_str, bip_str, cyc_str, tree_str, chrom_str, dia_str]:
            lbl = self.font_body.render(s, True, text_color)
            surface.blit(lbl, (self.x + 15, y_offset))
            y_offset += 22

        y_offset += 15
        pygame.draw.line(surface, cfg.THEME["panel_border"], (self.x + 15, y_offset), (self.x + self.width - 15, y_offset), 1)
        y_offset += 15

        # Centrality Heatmap Header
        heat_title = self.font_body.render("Centrality Heatmap", True, accent_color)
        surface.blit(heat_title, (self.x + 15, y_offset))
        y_offset += 30

        # 4 buttons: OFF, DEGREE, CLOSE, BETW
        modes = [("None", "OFF"), ("degree", "DEGREE"), ("closeness", "CLOSE"), ("betweenness", "BETW")]
        
        btn_w = (self.width - 40) // 2
        btn_h = 24
        
        for idx, (m_id, m_lbl) in enumerate(modes):
            col = idx % 2
            row = idx // 2
            bx = self.x + 15 + col * (btn_w + 10)
            by = y_offset + row * (btn_h + 8)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.heatmap_rects[m_id] = rect
            
            is_active = (centrality_mode == m_id or (centrality_mode is None and m_id == "None"))
            btn_bg = cfg.THEME["accent"] if is_active else cfg.THEME["panel_border"]
            btn_txt_color = cfg.THEME["sidebar_bg"] if is_active else cfg.THEME["text"]
            
            pygame.draw.rect(surface, btn_bg, rect, border_radius=4)
            lbl = self.font_body.render(m_lbl, True, btn_txt_color)
            surface.blit(lbl, lbl.get_rect(center=rect.center))

    def handle_click(self, mx: int, my: int) -> tuple[str, str] | None:
        for m_id, rect in self.heatmap_rects.items():
            if rect.collidepoint(mx, my):
                return ("centrality_mode", m_id)
        return None
