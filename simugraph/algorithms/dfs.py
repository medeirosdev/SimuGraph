from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class DFS(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Depth-First Search (DFS)"

    @property
    def description(self) -> str:
        return "Explores vertices by going as deep as possible before backtracking."

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Error: No source node selected.")]

        visited_set = set()
        stack = [source]
        parent = {source: None}
        
        states.append(AlgoState(
            visited=set(visited_set),
            frontier=set(stack),
            message=f"Initialize stack with source node '{graph.get_node(source).label}'",
            detail_text=f"Stack: {[graph.get_node(nid).label for nid in stack]}"
        ))
        
        while stack:
            u = stack.pop()
            if u not in visited_set:
                visited_set.add(u)
                
                highlighted_edges = set()
                for nid in visited_set:
                    p = parent.get(nid)
                    if p:
                        for e in graph.edges_between(nid, p):
                            highlighted_edges.add(e.id)
                            
                states.append(AlgoState(
                    visited=set(visited_set),
                    frontier=set(stack),
                    highlighted_edges=highlighted_edges,
                    message=f"Visited node '{graph.get_node(u).label}'",
                    detail_text=f"Stack: {[graph.get_node(nid).label for nid in stack]}"
                ))
                
                neighbors = []
                for edge in graph.edges_of(u):
                    neighbor_id = edge.v if edge.u == u else edge.u
                    if neighbor_id not in visited_set:
                        neighbors.append(neighbor_id)
                
                neighbors.sort(key=lambda nid: graph.get_node(nid).label, reverse=True)
                
                for neighbor_id in neighbors:
                    if neighbor_id not in stack:
                        stack.append(neighbor_id)
                        parent[neighbor_id] = u
                        
                        states.append(AlgoState(
                            visited=set(visited_set),
                            frontier=set(stack),
                            highlighted_edges=highlighted_edges,
                            message=f"Push neighbor '{graph.get_node(neighbor_id).label}' onto stack",
                            detail_text=f"Stack: {[graph.get_node(nid).label for nid in stack]}"
                        ))

        states.append(AlgoState(
            visited=set(visited_set),
            message="DFS Traversal Complete",
            detail_text="All reachable nodes explored."
        ))
        
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
