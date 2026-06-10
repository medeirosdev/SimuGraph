from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class BFS(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Breadth-First Search (BFS)"

    @property
    def description(self) -> str:
        return "Explores vertices level-by-level starting from the source node."

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Error: No source node selected.")]

        visited_set = set()
        frontier_set = {source}
        queue = [source]
        parent = {source: None}
        
        states.append(AlgoState(
            visited=set(visited_set),
            frontier=set(frontier_set),
            message=f"Initialize queue with source node '{graph.get_node(source).label}'",
            detail_text=f"Queue: {[graph.get_node(nid).label for nid in queue]}"
        ))
        
        while queue:
            u = queue.pop(0)
            frontier_set.discard(u)
            visited_set.add(u)
            
            states.append(AlgoState(
                visited=set(visited_set),
                frontier=set(frontier_set),
                message=f"Dequeued node '{graph.get_node(u).label}'",
                detail_text=f"Queue: {[graph.get_node(nid).label for nid in queue]}"
            ))
            
            for edge in graph.edges_of(u):
                neighbor_id = edge.v if edge.u == u else edge.u
                if neighbor_id not in visited_set and neighbor_id not in frontier_set:
                    frontier_set.add(neighbor_id)
                    queue.append(neighbor_id)
                    parent[neighbor_id] = u
                    
                    highlighted_edges = set()
                    for nid in frontier_set | visited_set:
                        curr_n = nid
                        while curr_n:
                            p = parent.get(curr_n)
                            if p:
                                for e in graph.edges_between(curr_n, p):
                                    highlighted_edges.add(e.id)
                            curr_n = p
                            
                    states.append(AlgoState(
                        visited=set(visited_set),
                        frontier=set(frontier_set),
                        highlighted_edges=highlighted_edges,
                        message=f"Discovered neighbor '{graph.get_node(neighbor_id).label}' from '{graph.get_node(u).label}'",
                        detail_text=f"Queue: {[graph.get_node(nid).label for nid in queue]}"
                    ))

        states.append(AlgoState(
            visited=set(visited_set),
            message="BFS Traversal Complete",
            detail_text="All reachable nodes explored."
        ))
        
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
