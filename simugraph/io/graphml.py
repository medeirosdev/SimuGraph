from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class GraphMLIO:
    @staticmethod
    def export_graphml(graph: Graph, filepath: str) -> None:
        root = ET.Element("graphml", {
            "xmlns": "http://graphml.graphdrawing.org/xmlns",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
        })
        
        ET.SubElement(root, "key", {"id": "d0", "for": "node", "attr.name": "label", "attr.type": "string"})
        ET.SubElement(root, "key", {"id": "d1", "for": "node", "attr.name": "x", "attr.type": "double"})
        ET.SubElement(root, "key", {"id": "d2", "for": "node", "attr.name": "y", "attr.type": "double"})
        ET.SubElement(root, "key", {"id": "d3", "for": "node", "attr.name": "color", "attr.type": "string"})
        ET.SubElement(root, "key", {"id": "d4", "for": "edge", "attr.name": "weight", "attr.type": "double"})
        
        is_directed = any(e.directed for e in graph.edges())
        edgedefault = "directed" if is_directed else "undirected"
        
        graph_elem = ET.SubElement(root, "graph", {"id": "G", "edgedefault": edgedefault})
        
        for node in graph.nodes():
            node_elem = ET.SubElement(graph_elem, "node", {"id": node.id})
            
            lbl_data = ET.SubElement(node_elem, "data", {"key": "d0"})
            lbl_data.text = node.label
            
            x_data = ET.SubElement(node_elem, "data", {"key": "d1"})
            x_data.text = str(node.x)
            
            y_data = ET.SubElement(node_elem, "data", {"key": "d2"})
            y_data.text = str(node.y)
            
            color_data = ET.SubElement(node_elem, "data", {"key": "d3"})
            color_data.text = f"{node.color[0]},{node.color[1]},{node.color[2]}"
            
        for edge in graph.edges():
            edge_elem = ET.SubElement(graph_elem, "edge", {
                "id": edge.id,
                "source": edge.u,
                "target": edge.v,
                "directed": "true" if edge.directed else "false"
            })
            
            w_data = ET.SubElement(edge_elem, "data", {"key": "d4"})
            w_data.text = str(edge.weight)
            
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ", level=0)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def import_graphml(graph: Graph, filepath: str) -> None:
        graph.clear()
        
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        key_map = {}
        for key in root.findall(".//{*}key") or root.findall("key"):
            key_id = key.get("id")
            attr_name = key.get("attr.name")
            if key_id and attr_name:
                key_map[key_id] = attr_name
                
        graph_elem = root.find(".//{*}graph") or root.find("graph")
        if graph_elem is None:
            return
            
        from simugraph.core.node import Node
        from simugraph.core.edge import Edge
        import random
        
        node_map = {}
        nodes_found = graph_elem.findall(".//{*}node") or graph_elem.findall("node")
        for node_elem in nodes_found:
            node_id = node_elem.get("id")
            if not node_id:
                continue
                
            label = ""
            x = random.uniform(100.0, 700.0)
            y = random.uniform(100.0, 500.0)
            color = (100, 180, 255)
            
            for data in node_elem.findall(".//{*}data") or node_elem.findall("data"):
                key_id = data.get("key")
                attr = key_map.get(key_id, key_id)
                if attr == "label" or key_id == "d0":
                    label = data.text or ""
                elif attr == "x" or key_id == "d1":
                    try:
                        x = float(data.text or "0")
                    except ValueError:
                        pass
                elif attr == "y" or key_id == "d2":
                    try:
                        y = float(data.text or "0")
                    except ValueError:
                        pass
                elif attr == "color" or key_id == "d3":
                    if data.text:
                        try:
                            parts = [int(p) for p in data.text.split(",")]
                            if len(parts) == 3:
                                color = tuple(parts)
                        except ValueError:
                            pass
                            
            node = Node(
                id=node_id,
                label=label,
                x=x,
                y=y,
                color=color
            )
            graph.add_node(node)
            node_map[node_id] = node
            
        edges_found = graph_elem.findall(".//{*}edge") or graph_elem.findall("edge")
        edge_counter = 0
        for edge_elem in edges_found:
            edge_id = edge_elem.get("id") or f"e_{edge_counter}"
            source = edge_elem.get("source")
            target = edge_elem.get("target")
            
            if not source or not target or source not in node_map or target not in node_map:
                continue
                
            directed_attr = edge_elem.get("directed")
            if directed_attr is not None:
                directed = directed_attr.lower() == "true"
            else:
                edgedefault = graph_elem.get("edgedefault", "undirected")
                directed = edgedefault.lower() == "directed"
                
            weight = 1.0
            for data in edge_elem.findall(".//{*}data") or edge_elem.findall("data"):
                key_id = data.get("key")
                attr = key_map.get(key_id, key_id)
                if attr == "weight" or key_id == "d4":
                    try:
                        weight = float(data.text or "1.0")
                    except ValueError:
                        pass
                        
            edge = Edge(
                id=edge_id,
                u=source,
                v=target,
                weight=weight,
                directed=directed
            )
            graph.add_edge(edge)
            edge_counter += 1
