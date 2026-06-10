import uuid
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.generators.random_graph import get_label

def generate_bipartite(n1: int, n2: int, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    
    if n1 <= 0 or n2 <= 0:
        return nodes, edges
        
    left_x = -200.0
    right_x = 200.0
    
    h1_spacing = height / (n1 + 1)
    h2_spacing = height / (n2 + 1)
    
    p1_nodes = []
    p2_nodes = []
    
    for i in range(n1):
        label = get_label(i)
        y = -height/2 + (i + 1) * h1_spacing
        node_id = str(uuid.uuid4())
        node = Node(id=node_id, label=label, x=left_x, y=y)
        nodes.append(node)
        p1_nodes.append(node)
        
    for j in range(n2):
        label = get_label(n1 + j)
        y = -height/2 + (j + 1) * h2_spacing
        node_id = str(uuid.uuid4())
        node = Node(id=node_id, label=label, x=right_x, y=y)
        nodes.append(node)
        p2_nodes.append(node)
        
    for u_node in p1_nodes:
        for v_node in p2_nodes:
            edge_id = str(uuid.uuid4())
            edges.append(Edge(id=edge_id, u=u_node.id, v=v_node.id, weight=1.0, directed=False))
            
    return nodes, edges
