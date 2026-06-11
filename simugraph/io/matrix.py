from __future__ import annotations
import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class AdjacencyMatrixIO:
    @staticmethod
    def export_matrix(graph: Graph, filepath: str, weighted: bool = True) -> None:
        nodes = sorted(list(graph.nodes()), key=lambda n: n.label or n.id)
        node_count = len(nodes)
        
        # Build matrix
        matrix = [[0.0 for _ in range(node_count)] for _ in range(node_count)]
        node_indices = {n.id: i for i, n in enumerate(nodes)}
        
        for edge in graph.edges():
            if edge.u in node_indices and edge.v in node_indices:
                u_idx = node_indices[edge.u]
                v_idx = node_indices[edge.v]
                w = edge.weight if weighted else 1.0
                matrix[u_idx][v_idx] = w
                if not edge.directed:
                    matrix[v_idx][u_idx] = w
                    
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            header = [""] + [n.label or f"Node_{i}" for i, n in enumerate(nodes)]
            writer.writerow(header)
            
            for i, n in enumerate(nodes):
                row = [n.label or f"Node_{i}"] + [str(matrix[i][j]) for j in range(node_count)]
                writer.writerow(row)

    @staticmethod
    def import_matrix(graph: Graph, filepath: str) -> None:
        graph.clear()
        
        with open(filepath, "r") as f:
            content = f.read()
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            
        if not lines:
            return
            
        # Parse CSV
        reader = csv.reader(lines)
        rows = list(reader)
        
        # Check if first cell of first row is empty, indicating header
        has_header = False
        if rows and len(rows[0]) > 0 and (rows[0][0] == "" or rows[0][0].lower() == "node" or len(rows[0]) == len(rows) + 1):
            has_header = True
            
        labels = []
        matrix_start_row = 0
        matrix_start_col = 0
        
        if has_header:
            labels = [lbl.strip() for lbl in rows[0][1:]]
            matrix_start_row = 1
            matrix_start_col = 1
        else:
            # Generate labels
            num_nodes = len(rows)
            labels = [f"N{i+1}" for i in range(num_nodes)]
            matrix_start_row = 0
            matrix_start_col = 0
            
        # Create nodes in a circle layout initially
        import math
        from simugraph.core.node import Node
        node_list = []
        num_nodes = len(labels)
        
        cx, cy = 400.0, 300.0
        radius = 200.0
        
        for i, label in enumerate(labels):
            angle = i * (2 * math.pi / max(1, num_nodes))
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            node = Node(
                id=f"node_{i}",
                label=label,
                x=x,
                y=y
            )
            graph.add_node(node)
            node_list.append(node)
            
        # Parse edges
        num_cols = len(rows[matrix_start_row]) - matrix_start_col
        num_rows = len(rows) - matrix_start_row
        size = min(num_rows, num_cols)
        
        matrix_vals = [[0.0 for _ in range(size)] for _ in range(size)]
        for r in range(size):
            row_data = rows[matrix_start_row + r]
            for c in range(size):
                val_str = row_data[matrix_start_col + c]
                try:
                    matrix_vals[r][c] = float(val_str)
                except ValueError:
                    matrix_vals[r][c] = 0.0
                    
        # Check symmetry
        is_symmetric = True
        for r in range(size):
            for c in range(r + 1, size):
                if abs(matrix_vals[r][c] - matrix_vals[c][r]) > 1e-9:
                    is_symmetric = False
                    break
            if not is_symmetric:
                break
                
        # Add edges
        from simugraph.core.edge import Edge
        edge_counter = 0
        for r in range(size):
            c_start = r if is_symmetric else 0
            for c in range(c_start, size):
                val = matrix_vals[r][c]
                if val != 0.0:
                    edge = Edge(
                        id=f"edge_{edge_counter}",
                        u=node_list[r].id,
                        v=node_list[c].id,
                        weight=val,
                        directed=not is_symmetric
                    )
                    graph.add_edge(edge)
                    edge_counter += 1
