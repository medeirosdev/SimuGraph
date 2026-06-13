from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class ClipboardIO:
    @staticmethod
    def get_clipboard() -> str:
        """Retrieve text from the system clipboard with Pygame/Tkinter fallbacks."""
        # Try pygame scrap first (native to active game loop)
        try:
            import pygame
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            val = pygame.scrap.get(pygame.SCRAP_TEXT)
            if val:
                return val.decode("utf-8").strip("\x00")
        except Exception:
            pass
            
        # Try tkinter fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
        except Exception:
            return ""

    @staticmethod
    def set_clipboard(text: str) -> None:
        """Write text to the system clipboard with Pygame/Tkinter fallbacks."""
        # Try pygame scrap first
        try:
            import pygame
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
            return
        except Exception:
            pass

        # Try tkinter fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
        except Exception:
            pass

    @staticmethod
    def export_tuples(graph: Graph) -> str:
        """Export the graph as a Python list of tuples: [(u, v, weight), ...]"""
        edges = []
        for edge in graph.edges():
            u_node = graph.get_node(edge.u)
            v_node = graph.get_node(edge.v)
            if u_node and v_node:
                # Include directed flag if edge is directed
                if edge.directed:
                    edges.append((u_node.label, v_node.label, edge.weight, True))
                else:
                    edges.append((u_node.label, v_node.label, edge.weight))
        return repr(edges)

    @staticmethod
    def import_tuples(graph: Graph, text: str, default_directed: bool = False) -> None:
        """
        Import the graph from a Python list of tuples.
        Supports:
          - [(u, v), ...]
          - [(u, v, weight), ...]
          - [(u, v, weight, directed), ...]
        """
        import ast
        try:
            data = ast.literal_eval(text.strip())
        except Exception as e:
            raise ValueError(f"Invalid Python format: {e}")
            
        if not isinstance(data, list):
            raise ValueError("Parsed data is not a Python list.")
            
        graph.clear()
        
        # Parse items and collect unique labels
        labels = set()
        edges_to_add = []
        for item in data:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            u_lbl = str(item[0]).strip()
            v_lbl = str(item[1]).strip()
            if not u_lbl or not v_lbl:
                continue
                
            weight = 1.0
            if len(item) > 2:
                try:
                    weight = float(item[2])
                except ValueError:
                    weight = 1.0
                    
            directed = bool(item[3]) if len(item) > 3 else default_directed
            
            labels.add(u_lbl)
            labels.add(v_lbl)
            edges_to_add.append((u_lbl, v_lbl, weight, directed))
            
        # Place nodes in a neat circle layout initially
        import math
        from simugraph.core.node import Node
        
        labels_list = sorted(list(labels))
        num_nodes = len(labels_list)
        cx, cy = 400.0, 300.0
        radius = 200.0
        
        node_map = {}
        for i, lbl in enumerate(labels_list):
            angle = i * (2 * math.pi / max(1, num_nodes))
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            node = Node(
                id=f"node_{i}",
                label=lbl,
                x=x,
                y=y
            )
            graph.add_node(node)
            node_map[lbl] = node
            
        # Create edges
        from simugraph.core.edge import Edge
        for idx, (u_lbl, v_lbl, w, d) in enumerate(edges_to_add):
            u_node = node_map[u_lbl]
            v_node = node_map[v_lbl]
            edge = Edge(
                id=f"edge_{idx}",
                u=u_node.id,
                v=v_node.id,
                weight=w,
                directed=d
            )
            graph.add_edge(edge)
