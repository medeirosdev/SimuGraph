import math
import uuid
import random
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.generators.random_graph import get_label

def generate_barabasi_albert(n: int, m: int, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    
    if n <= 0 or m <= 0 or m >= n:
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
        
    degrees = {nodes[idx].id: 0 for idx in range(n)}
    
    for i in range(m + 1):
        for j in range(i + 1, m + 1):
            edge_id = str(uuid.uuid4())
            edges.append(Edge(id=edge_id, u=nodes[i].id, v=nodes[j].id, weight=1.0, directed=False))
            degrees[nodes[i].id] += 1
            degrees[nodes[j].id] += 1
            
    for i in range(m + 1, n):
        existing_ids = [nodes[j].id for j in range(i)]
        existing_degrees = [degrees[node_id] for node_id in existing_ids]
        total_deg = sum(existing_degrees)
        
        if total_deg == 0:
            targets = random.sample(existing_ids, m)
        else:
            targets = []
            while len(targets) < m:
                r = random.uniform(0, total_deg)
                curr_sum = 0
                for node_id, deg in zip(existing_ids, existing_degrees):
                    curr_sum += deg
                    if curr_sum >= r:
                        if node_id not in targets:
                            targets.append(node_id)
                        break
                        
        new_node_id = nodes[i].id
        for target_id in targets:
            edge_id = str(uuid.uuid4())
            edges.append(Edge(id=edge_id, u=new_node_id, v=target_id, weight=1.0, directed=False))
            degrees[new_node_id] += 1
            degrees[target_id] += 1
            
    return nodes, edges
