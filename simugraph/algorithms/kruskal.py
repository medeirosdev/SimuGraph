from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class Kruskal(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Kruskal's MST"

    @property
    def description(self) -> str:
        return "Finds the Minimum Spanning Tree (MST) of a connected undirected graph by sorting edges by weight."

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = list(graph.nodes())
        edges_list = list(graph.edges())
        
        edges_sorted = sorted(edges_list, key=lambda e: e.weight)
        
        parent = {n.id: n.id for n in nodes_list}
        
        def find(i):
            path = []
            while parent[i] != i:
                path.append(i)
                i = parent[i]
            for node in path:
                parent[node] = i
            return i
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        mst_edges = set()
        visited_nodes = set()
        
        def get_mst_text():
            lines = ["MST Edges:"]
            for eid in mst_edges:
                e = next((x for x in edges_list if x.id == eid), None)
                if e:
                    u_lbl = graph.get_node(e.u).label if graph.get_node(e.u) else ""
                    v_lbl = graph.get_node(e.v).label if graph.get_node(e.v) else ""
                    lines.append(f"  {u_lbl} - {v_lbl} (weight: {e.weight})")
            return "\n".join(lines)

        states.append(AlgoState(
            message="Sort edges by weight. Initializing empty MST.",
            detail_text=get_mst_text()
        ))
        
        for edge in edges_sorted:
            u_node = graph.get_node(edge.u)
            v_node = graph.get_node(edge.v)
            if not u_node or not v_node:
                continue
                
            states.append(AlgoState(
                visited=set(visited_nodes),
                highlighted_edges=set(mst_edges) | {edge.id},
                message=f"Checking edge {u_node.label} - {v_node.label} (weight {edge.weight})",
                detail_text=get_mst_text()
            ))
            
            if union(edge.u, edge.v):
                mst_edges.add(edge.id)
                visited_nodes.add(edge.u)
                visited_nodes.add(edge.v)
                states.append(AlgoState(
                    visited=set(visited_nodes),
                    highlighted_edges=set(mst_edges),
                    message=f"Added edge {u_node.label} - {v_node.label} to MST (no cycle formed)",
                    detail_text=get_mst_text()
                ))
            else:
                states.append(AlgoState(
                    visited=set(visited_nodes),
                    highlighted_edges=set(mst_edges),
                    message=f"Skipped edge {u_node.label} - {v_node.label}: adding it would form a cycle",
                    detail_text=get_mst_text()
                ))

        states.append(AlgoState(
            visited=set(visited_nodes),
            highlighted_edges=set(mst_edges),
            message="Kruskal's MST Algorithm Complete",
            detail_text=get_mst_text()
        ))
        
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
