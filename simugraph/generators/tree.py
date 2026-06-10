import uuid
import random
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.generators.random_graph import get_label

def generate_tree(n: int, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    
    if n <= 0:
        return nodes, edges
        
    for idx in range(n):
        label = get_label(idx)
        node_id = str(uuid.uuid4())
        nodes.append(Node(id=node_id, label=label, x=0.0, y=0.0))
        
    adjacency = {idx: [] for idx in range(n)}
    for idx in range(1, n):
        parent = random.randint(0, idx - 1)
        adjacency[parent].append(idx)
        adjacency[idx].append(parent)
        edge_id = str(uuid.uuid4())
        edges.append(Edge(id=edge_id, u=nodes[parent].id, v=nodes[idx].id, weight=1.0, directed=False))
        
    depths = {0: 0}
    queue = [0]
    visited = {0}
    levels = {}
    
    while queue:
        curr = queue.pop(0)
        d = depths[curr]
        levels.setdefault(d, []).append(curr)
        for neighbor in adjacency[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                depths[neighbor] = d + 1
                queue.append(neighbor)
                
    max_depth = max(depths.values()) if depths else 0
    y_spacing = (height - 100) / max(1, max_depth)
    
    for d, nodes_at_depth in levels.items():
        count = len(nodes_at_depth)
        x_spacing = width / (count + 1)
        y = -height/2 + 50 + d * y_spacing
        for idx_in_level, node_idx in enumerate(nodes_at_depth):
            x = -width/2 + (idx_in_level + 1) * x_spacing
            nodes[node_idx].x = x
            nodes[node_idx].y = y
            
    return nodes, edges
