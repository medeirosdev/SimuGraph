from __future__ import annotations
import xml.etree.ElementTree as ET
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class GexfIO:
    @staticmethod
    def export_gexf(graph: Graph, filepath: str) -> None:
        root = ET.Element("gexf", {
            "xmlns": "http://www.gexf.net/1.2draft",
            "xmlns:viz": "http://www.gexf.net/1.2draft/viz",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd",
            "version": "1.2"
        })
        
        meta = ET.SubElement(root, "meta", {
            "lastmodifieddate": datetime.date.today().isoformat()
        })
        creator = ET.SubElement(meta, "creator")
        creator.text = "SimuGraph"
        description = ET.SubElement(meta, "description")
        description.text = "Graph exported from SimuGraph"
        
        is_directed = any(e.directed for e in graph.edges())
        defaultedgetype = "directed" if is_directed else "undirected"
        
        graph_elem = ET.SubElement(root, "graph", {
            "defaultedgetype": defaultedgetype,
            "mode": "static"
        })
        
        nodes_elem = ET.SubElement(graph_elem, "nodes")
        for node in graph.nodes():
            node_elem = ET.SubElement(nodes_elem, "node", {
                "id": node.id,
                "label": node.label or ""
            })
            
            ET.SubElement(node_elem, "{http://www.gexf.net/1.2draft/viz}position", {
                "x": str(node.x),
                "y": str(-node.y),
                "z": "0.0"
            })
            
            ET.SubElement(node_elem, "{http://www.gexf.net/1.2draft/viz}color", {
                "r": str(node.color[0]),
                "g": str(node.color[1]),
                "b": str(node.color[2]),
                "a": "1.0"
            })
            
            ET.SubElement(node_elem, "{http://www.gexf.net/1.2draft/viz}size", {
                "value": str(node.radius)
            })
            
        edges_elem = ET.SubElement(graph_elem, "edges")
        for edge in graph.edges():
            edge_elem = ET.SubElement(edges_elem, "edge", {
                "id": edge.id,
                "source": edge.u,
                "target": edge.v,
                "weight": str(edge.weight),
                "type": "directed" if edge.directed else "undirected"
            })
            
            ET.SubElement(edge_elem, "{http://www.gexf.net/1.2draft/viz}color", {
                "r": str(edge.color[0]),
                "g": str(edge.color[1]),
                "b": str(edge.color[2]),
                "a": "1.0"
            })
            
        ET.register_namespace("viz", "http://www.gexf.net/1.2draft/viz")
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
