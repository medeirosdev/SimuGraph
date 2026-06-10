import uuid
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.generators.random_graph import get_label

def generate_grid(rows: int, cols: int, width: int = 800, height: int = 600) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    
    if rows <= 0 or cols <= 0:
        return nodes, edges
        
    x_spacing = width / (cols + 1) if cols > 1 else width
    y_spacing = height / (rows + 1) if rows > 1 else height
    
    grid_nodes = []
    for r in range(rows):
        row_list = []
        for c in range(cols):
            idx = r * cols + c
            label = get_label(idx)
            
            x = -width/2 + (c + 1) * x_spacing if cols > 1 else 0.0
            y = -height/2 + (r + 1) * y_spacing if rows > 1 else 0.0
            
            node_id = str(uuid.uuid4())
            node = Node(id=node_id, label=label, x=x, y=y)
            nodes.append(node)
            row_list.append(node)
        grid_nodes.append(row_list)
        
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                edge_id = str(uuid.uuid4())
                edges.append(Edge(id=edge_id, u=grid_nodes[r][c].id, v=grid_nodes[r][c+1].id, weight=1.0, directed=False))
            if r + 1 < rows:
                edge_id = str(uuid.uuid4())
                edges.append(Edge(id=edge_id, u=grid_nodes[r][c].id, v=grid_nodes[r+1][c].id, weight=1.0, directed=False))
                
    return nodes, edges
