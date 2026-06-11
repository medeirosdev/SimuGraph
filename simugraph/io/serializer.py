from __future__ import annotations
import json
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph
    from simugraph.camera import Camera

class GraphSerializer:
    @staticmethod
    def to_json(graph: Graph, camera: Camera | None = None) -> str:
        data = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.datetime.now().isoformat(),
                "node_count": len(list(graph.nodes())),
                "edge_count": len(list(graph.edges()))
            },
            "nodes": [],
            "edges": []
        }
        
        if camera:
            data["camera"] = {
                "zoom": camera.zoom,
                "offset_x": camera.offset_x,
                "offset_y": camera.offset_y
            }
        else:
            data["camera"] = None
            
        for node in graph.nodes():
            data["nodes"].append({
                "id": node.id,
                "label": node.label,
                "x": node.x,
                "y": node.y,
                "color": list(node.color),
                "radius": node.radius,
                "pinned": node.pinned
            })
            
        for edge in graph.edges():
            data["edges"].append({
                "id": edge.id,
                "u": edge.u,
                "v": edge.v,
                "weight": edge.weight,
                "directed": edge.directed,
                "color": list(edge.color)
            })
            
        return json.dumps(data, indent=4)

    @staticmethod
    def from_json(json_str: str, graph: Graph, camera: Camera | None = None) -> None:
        data = json.loads(json_str)
        
        # Clear existing graph
        graph.clear()
        
        # Import camera settings if present
        if camera and data.get("camera"):
            cam_data = data["camera"]
            camera.zoom = cam_data.get("zoom", 1.0)
            camera.offset_x = cam_data.get("offset_x", 0.0)
            camera.offset_y = cam_data.get("offset_y", 0.0)
            
        # Add nodes
        from simugraph.core.node import Node
        for n_data in data.get("nodes", []):
            node = Node(
                id=n_data["id"],
                label=n_data["label"],
                x=n_data["x"],
                y=n_data["y"],
                color=tuple(n_data["color"]),
                radius=n_data.get("radius", 22),
                pinned=n_data.get("pinned", False)
            )
            graph.add_node(node)
            
        # Add edges
        from simugraph.core.edge import Edge
        for e_data in data.get("edges", []):
            edge = Edge(
                id=e_data["id"],
                u=e_data["u"],
                v=e_data["v"],
                weight=e_data["weight"],
                directed=e_data["directed"],
                color=tuple(e_data["color"])
            )
            graph.add_edge(edge)
