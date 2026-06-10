from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class Dijkstra(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Dijkstra's Algorithm"

    @property
    def description(self) -> str:
        return "Finds the shortest path from a source node to all other nodes on a weighted graph."

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Error: No source node selected.")]

        distances = {n.id: float('inf') for n in graph.nodes()}
        distances[source] = 0.0
        
        visited_set = set()
        unvisited = set(n.id for n in graph.nodes())
        parent = {n.id: None for n in graph.nodes()}
        
        def format_dist_text():
            lines = ["Distances:"]
            for nid, dist in sorted(distances.items(), key=lambda x: graph.get_node(x[0]).label if graph.get_node(x[0]) else ""):
                node = graph.get_node(nid)
                if node:
                    lines.append(f"  {node.label}: {dist}")
            return "\n".join(lines)

        states.append(AlgoState(
            visited=set(visited_set),
            frontier=set(unvisited),
            distances=dict(distances),
            message=f"Initialize distances. Set dist({graph.get_node(source).label}) = 0",
            detail_text=format_dist_text()
        ))
        
        while unvisited:
            u = min(unvisited, key=lambda nid: distances[nid])
            if distances[u] == float('inf'):
                break
                
            unvisited.remove(u)
            visited_set.add(u)
            
            highlighted_edges = set()
            for nid in visited_set:
                p = parent.get(nid)
                if p:
                    for e in graph.edges_between(nid, p):
                        highlighted_edges.add(e.id)
                        
            states.append(AlgoState(
                visited=set(visited_set),
                frontier=set(unvisited),
                distances=dict(distances),
                highlighted_edges=highlighted_edges,
                message=f"Visited node '{graph.get_node(u).label}' (closest unvisited)",
                detail_text=format_dist_text()
            ))
            
            for edge in graph.edges_of(u):
                neighbor_id = edge.v if edge.u == u else edge.u
                if neighbor_id in unvisited:
                    alt = distances[u] + edge.weight
                    if alt < distances[neighbor_id]:
                        old_dist = distances[neighbor_id]
                        distances[neighbor_id] = alt
                        parent[neighbor_id] = u
                        
                        relax_edges = set(highlighted_edges)
                        relax_edges.add(edge.id)
                        
                        states.append(AlgoState(
                            visited=set(visited_set),
                            frontier=set(unvisited),
                            distances=dict(distances),
                            highlighted_edges=relax_edges,
                            message=f"Relax edge to '{graph.get_node(neighbor_id).label}': new dist = {alt} (was {old_dist})",
                            detail_text=format_dist_text()
                        ))

        final_edges = set()
        for nid in visited_set:
            p = parent.get(nid)
            if p:
                for e in graph.edges_between(nid, p):
                    final_edges.add(e.id)

        states.append(AlgoState(
            visited=set(visited_set),
            distances=dict(distances),
            highlighted_edges=final_edges,
            message="Dijkstra Shortest Path Tree Complete",
            detail_text=format_dist_text()
        ))
        
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
