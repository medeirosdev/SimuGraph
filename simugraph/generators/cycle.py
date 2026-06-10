import math
import uuid
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.generators.random_graph import get_label

def generate_cycle(n: int, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    
    if n <= 0:
        return nodes, edges
        
    radius = min(width, height) * 0.4
    center_x, center_y = 0.0, 0.0
    
    for idx in range(n):
        angle = 2 * math.pi * idx / n
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        label = get_label(idx)
        node_id = str(uuid.uuid4())
        nodes.append(Node(id=node_id, label=label, x=x, y=y))
        
    for idx in range(n):
        next_idx = (idx + 1) % n
        edge_id = str(uuid.uuid4())
        edges.append(Edge(id=edge_id, u=nodes[idx].id, v=nodes[next_idx].id, weight=1.0, directed=False))
        
    return nodes, edges
