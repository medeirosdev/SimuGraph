from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class DotFormatIO:
    @staticmethod
    def export_dot(graph: Graph, filepath: str) -> None:
        is_directed = any(e.directed for e in graph.edges())
        
        lines = []
        if is_directed:
            lines.append("digraph G {")
            edge_op = "->"
        else:
            lines.append("graph G {")
            edge_op = "--"
            
        for node in graph.nodes():
            label = node.label or ""
            pos_str = f"{node.x/72.0},{node.y/72.0}!"
            hex_color = f"#{node.color[0]:02x}{node.color[1]:02x}{node.color[2]:02x}"
            lines.append(f'    "{node.id}" [label="{label}", pos="{pos_str}", fillcolor="{hex_color}", style="filled", width={node.radius/36.0}];')
            
        for edge in graph.edges():
            hex_color = f"#{edge.color[0]:02x}{edge.color[1]:02x}{edge.color[2]:02x}"
            lines.append(f'    "{edge.u}" {edge_op} "{edge.v}" [weight={edge.weight}, label="{edge.weight}", color="{hex_color}"];')
            
        lines.append("}")
        
        with open(filepath, "w") as f:
            f.write("\n".join(lines) + "\n")
