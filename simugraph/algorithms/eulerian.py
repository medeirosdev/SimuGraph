from __future__ import annotations
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class EulerianPathCircuit(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Eulerian Cycle/Path"

    @property
    def description(self) -> str:
        return "Hierholzer's algorithm to trace an Eulerian Cycle or Path"

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = sorted(list(graph.nodes()), key=lambda n: n.label)
        if not nodes_list:
            return [AlgoState(message="Empty graph.", step_index=1, total_steps=1)]

        # Determine if Eulerian Path or Circuit exists
        # Multi-graph adjacency copy to trace (since we traverse edges and remove them)
        adj: dict[str, list[tuple[str, str, bool]]] = {n.id: [] for n in nodes_list} # node_id -> list of (neighbor_id, edge_id, edge_directed)
        edge_map = {}
        for edge in graph.edges():
            edge_map[edge.id] = edge
            adj[edge.u].append((edge.v, edge.id, edge.directed))
            if not edge.directed:
                adj[edge.v].append((edge.u, edge.id, edge.directed))

        # Check degree conditions
        has_directed = any(edge.directed for edge in graph.edges())
        
        start_node = None
        type_str = ""
        possible = True

        if has_directed:
            # Directed graph conditions:
            # 1. At most one vertex has out_degree - in_degree = 1 (start)
            # 2. At most one vertex has in_degree - out_degree = 1 (end)
            # 3. All other vertices have in_degree == out_degree
            in_deg = {n.id: 0 for n in nodes_list}
            out_deg = {n.id: 0 for n in nodes_list}
            for edge in graph.edges():
                out_deg[edge.u] += 1
                in_deg[edge.v] += 1
            
            start_candidates = []
            end_candidates = []
            mismatches = 0
            for nid in in_deg:
                diff = out_deg[nid] - in_deg[nid]
                if diff == 1:
                    start_candidates.append(nid)
                elif diff == -1:
                    end_candidates.append(nid)
                elif diff != 0:
                    mismatches += 1
            
            if mismatches == 0 and len(start_candidates) == 0 and len(end_candidates) == 0:
                # Eulerian Circuit
                start_node = nodes_list[0].id
                type_str = "Eulerian Circuit"
            elif len(start_candidates) == 1 and len(end_candidates) == 1 and mismatches == 0:
                start_node = start_candidates[0]
                type_str = "Eulerian Path"
            else:
                possible = False
        else:
            # Undirected graph conditions:
            # 1. Every vertex has an even degree (Eulerian Circuit) OR
            # 2. Exactly zero or two vertices have an odd degree (Eulerian Path)
            odd_deg = []
            for n in nodes_list:
                deg = len(adj[n.id])
                if deg % 2 != 0:
                    odd_deg.append(n.id)
            
            if len(odd_deg) == 0:
                start_node = nodes_list[0].id
                type_str = "Eulerian Circuit"
            elif len(odd_deg) == 2:
                start_node = odd_deg[0]
                type_str = "Eulerian Path"
            else:
                possible = False

        if not possible or start_node is None:
            return [AlgoState(
                message="This graph does not contain an Eulerian Path or Eulerian Circuit.",
                step_index=1,
                total_steps=1,
                detail_text="Conditions check failed:\n- Undirected graph must have exactly 0 or 2 vertices of odd degree.\n- Directed graph must satisfy in-degree & out-degree balance constraints."
            )]

        # Hierholzer's algorithm to trace circuit/path
        # Keep track of active path/circuit
        curr_path = [start_node]
        circuit = []
        
        # Keep track of unused edges
        remaining_edges = {e.id for e in graph.edges()}

        def get_detail_text(curr_n: str | None) -> str:
            lines = []
            lines.append(f"Format: {type_str}")
            if curr_n:
                lines.append(f"Current Position: {graph.get_node(curr_n).label}\n")
            lines.append(f"Trace stack: {' -> '.join([graph.get_node(x).label for x in curr_path if graph.get_node(x)])}")
            lines.append(f"Final Circuit / Path: {' -> '.join([graph.get_node(x).label for x in reversed(circuit) if graph.get_node(x)])}\n")
            lines.append(f"Remaining Untraversed Edges: {len(remaining_edges)} / {len(graph.edges())}")
            return "\n".join(lines)

        states.append(AlgoState(
            message=f"Starting Hierholzer's algorithm to trace {type_str} from {graph.get_node(start_node).label}.",
            detail_text=get_detail_text(start_node)
        ))

        while curr_path:
            curr = curr_path[-1]
            
            # Find an unused edge from current
            found_edge = False
            for neighbor_id, edge_id, directed in adj[curr]:
                if edge_id in remaining_edges:
                    remaining_edges.remove(edge_id)
                    curr_path.append(neighbor_id)
                    found_edge = True
                    
                    states.append(AlgoState(
                        visited={curr, neighbor_id},
                        highlighted_edges=set(graph.edges()) - remaining_edges,
                        message=f"Traversing edge {graph.get_node(curr).label} -> {graph.get_node(neighbor_id).label}.",
                        detail_text=get_detail_text(neighbor_id)
                    ))
                    break
            
            if not found_edge:
                popped = curr_path.pop()
                circuit.append(popped)
                states.append(AlgoState(
                    visited={popped},
                    highlighted_edges=set(graph.edges()) - remaining_edges,
                    message=f"No untraversed edges from {graph.get_node(popped).label}. Backtracking and committing to circuit.",
                    detail_text=get_detail_text(popped)
                ))

        # Reconstructed final path/circuit (Hierholzer output is in reverse)
        final_path = list(reversed(circuit))
        
        # Highlighting final traversed sequence in order
        highlighted_edges = set()
        for i in range(len(final_path) - 1):
            u, v = final_path[i], final_path[i+1]
            edges = graph.edges_between(u, v)
            if edges:
                highlighted_edges.add(edges[0].id)

        states.append(AlgoState(
            path=final_path,
            highlighted_edges=highlighted_edges,
            message=f"Eulerian cycle/path tracing complete: {' -> '.join([graph.get_node(x).label for x in final_path if graph.get_node(x)])}",
            detail_text=get_detail_text(None)
        ))

        # Update step indexes
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
