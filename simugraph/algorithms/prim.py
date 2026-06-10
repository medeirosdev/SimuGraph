from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class Prim(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Prim's MST"

    @property
    def description(self) -> str:
        return "Finds the Minimum Spanning Tree (MST) of a connected undirected graph starting from a selected source node."

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Error: No source node selected.")]

        visited_nodes = {source}
        mst_edges = set()
        all_edges = list(graph.edges())
        
        def get_mst_text():
            lines = ["MST Edges:"]
            for eid in mst_edges:
                e = next((x for x in all_edges if x.id == eid), None)
                if e:
                    u_lbl = graph.get_node(e.u).label if graph.get_node(e.u) else ""
                    v_lbl = graph.get_node(e.v).label if graph.get_node(e.v) else ""
                    lines.append(f"  {u_lbl} - {v_lbl} (weight: {e.weight})")
            return "\n".join(lines)

        states.append(AlgoState(
            visited=set(visited_nodes),
            message=f"Initialize MST with source node '{graph.get_node(source).label}'",
            detail_text=get_mst_text()
        ))

        n = len(graph.nodes())
        while len(visited_nodes) < n:
            min_edge = None
            min_weight = float('inf')
            
            frontier_edges = set()
            for edge in all_edges:
                u_in = edge.u in visited_nodes
                v_in = edge.v in visited_nodes
                if u_in != v_in:
                    frontier_edges.add(edge.id)
                    if edge.weight < min_weight:
                        min_weight = edge.weight
                        min_edge = edge
                        
            if not min_edge:
                states.append(AlgoState(
                    visited=set(visited_nodes),
                    highlighted_edges=set(mst_edges),
                    message="Graph is disconnected. Prim's MST completed early.",
                    detail_text=get_mst_text()
                ))
                break

            candidates_nodes = set()
            for eid in frontier_edges:
                e = next((x for x in all_edges if x.id == eid), None)
                if e:
                    if e.u not in visited_nodes:
                        candidates_nodes.add(e.u)
                    if e.v not in visited_nodes:
                        candidates_nodes.add(e.v)

            states.append(AlgoState(
                visited=set(visited_nodes),
                frontier=candidates_nodes,
                highlighted_edges=set(mst_edges) | {min_edge.id},
                message=f"Examine candidate frontier edges. Selected minimum weight: {graph.get_node(min_edge.u).label} - {graph.get_node(min_edge.v).label} (weight {min_edge.weight})",
                detail_text=get_mst_text()
            ))
            
            new_node = min_edge.v if min_edge.u in visited_nodes else min_edge.u
            visited_nodes.add(new_node)
            mst_edges.add(min_edge.id)
            
            states.append(AlgoState(
                visited=set(visited_nodes),
                highlighted_edges=set(mst_edges),
                message=f"Added node '{graph.get_node(new_node).label}' and edge to MST",
                detail_text=get_mst_text()
            ))

        states.append(AlgoState(
            visited=set(visited_nodes),
            highlighted_edges=set(mst_edges),
            message="Prim's MST Algorithm Complete",
            detail_text=get_mst_text()
        ))
        
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
