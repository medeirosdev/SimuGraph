import math
import random
import uuid
from simugraph.core.node import Node
from simugraph.core.edge import Edge

def generate_random_graph(n: int, p: float, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
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
        
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                edge_id = str(uuid.uuid4())
                edges.append(Edge(id=edge_id, u=nodes[i].id, v=nodes[j].id, weight=1.0, directed=False))
                
    return nodes, edges

def get_label(idx: int) -> str:
    label = ""
    while idx >= 0:
        label = chr(65 + (idx % 26)) + label
        idx = (idx // 26) - 1
    return label
