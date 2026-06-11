from __future__ import annotations
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class FloydWarshall(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Floyd-Warshall"

    @property
    def description(self) -> str:
        return "All-Pairs Shortest Path algorithm"

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = sorted(list(graph.nodes()), key=lambda n: n.label)
        n = len(nodes_list)
        if n == 0:
            return [AlgoState(message="Empty graph.", step_index=1, total_steps=1)]

        node_ids = [node.id for node in nodes_list]
        id_to_idx = {nid: i for i, nid in enumerate(node_ids)}

        # Initialize distance matrix
        dist = [[float('inf')] * n for _ in range(n)]
        next_node = [[None] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0.0

        # Build initial edges
        for edge in graph.edges():
            u_idx = id_to_idx.get(edge.u)
            v_idx = id_to_idx.get(edge.v)
            if u_idx is not None and v_idx is not None:
                # If there are parallel edges, keep the minimum weight
                if edge.weight < dist[u_idx][v_idx]:
                    dist[u_idx][v_idx] = float(edge.weight)
                    next_node[u_idx][v_idx] = edge.v
                if not edge.directed:
                    if edge.weight < dist[v_idx][u_idx]:
                        dist[v_idx][u_idx] = float(edge.weight)
                        next_node[v_idx][u_idx] = edge.u

        def format_matrix(d_mat) -> str:
            lines = []
            # Header
            header = "    " + " ".join(f"{nodes_list[i].label:>4}" for i in range(n))
            lines.append(header)
            for i in range(n):
                row_str = f"{nodes_list[i].label}: "
                row_vals = []
                for j in range(n):
                    val = d_mat[i][j]
                    if val == float('inf'):
                        row_vals.append(" inf")
                    else:
                        row_vals.append(f"{val:>4.1f}" if val % 1 != 0 else f"{int(val):>4}")
                row_str += " ".join(row_vals)
                lines.append(row_str)
            return "\n".join(lines)

        # Step 0: Initial matrix
        initial_detail = "Initial Distance Matrix:\n\n" + format_matrix(dist)
        states.append(AlgoState(
            message="Initializing Floyd-Warshall distance matrix.",
            detail_text=initial_detail
        ))

        # Iterations
        for k in range(n):
            pivot_node = nodes_list[k]
            for u in range(n):
                row_node = nodes_list[u]
                
                # Check for changes in this row
                any_change = False
                for v in range(n):
                    if dist[u][k] != float('inf') and dist[k][v] != float('inf'):
                        if dist[u][k] + dist[k][v] < dist[u][v]:
                            dist[u][v] = dist[u][k] + dist[k][v]
                            next_node[u][v] = next_node[u][k]
                            any_change = True
                
                # Build state representing row-by-row updates
                state_detail = f"Pivot node (k): {pivot_node.label}\nRow node (u): {row_node.label}\n\n" + format_matrix(dist)
                msg = f"Checking row {row_node.label} using pivot {pivot_node.label}."
                if any_change:
                    msg += " Distances updated."
                
                # Highlights
                visited = {row_node.id}
                frontier = {pivot_node.id}
                
                states.append(AlgoState(
                    visited=visited,
                    frontier=frontier,
                    message=msg,
                    detail_text=state_detail
                ))

        # Final state
        final_detail = "Final All-Pairs Shortest Path Matrix:\n\n" + format_matrix(dist)
        states.append(AlgoState(
            message="Floyd-Warshall complete.",
            detail_text=final_detail
        ))

        # Update step indexes
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
