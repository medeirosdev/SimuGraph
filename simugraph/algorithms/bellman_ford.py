from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class BellmanFord(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Bellman-Ford Algorithm"

    @property
    def description(self) -> str:
        return "Finds shortest paths from a source node, supporting negative edge weights and detecting negative cycles."

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Error: No source node selected.")]

        distances = {n.id: float('inf') for n in graph.nodes()}
        distances[source] = 0.0
        parent = {n.id: None for n in graph.nodes()}
        
        def format_dist_text():
            lines = ["Distances:"]
            for nid, dist in sorted(distances.items(), key=lambda x: graph.get_node(x[0]).label if graph.get_node(x[0]) else ""):
                node = graph.get_node(nid)
                if node:
                    lines.append(f"  {node.label}: {dist}")
            return "\n".join(lines)

        states.append(AlgoState(
            distances=dict(distances),
            message=f"Initialize distances. Set dist({graph.get_node(source).label}) = 0",
            detail_text=format_dist_text()
        ))

        nodes_list = list(graph.nodes())
        edges_list = list(graph.edges())
        n = len(nodes_list)
        
        for i in range(n - 1):
            relaxed_any = False
            states.append(AlgoState(
                distances=dict(distances),
                message=f"Start iteration {i + 1} of {n - 1}",
                detail_text=format_dist_text()
            ))
            
            for edge in edges_list:
                u = edge.u
                v = edge.v
                
                if distances[u] != float('inf') and distances[u] + edge.weight < distances[v]:
                    old_dist = distances[v]
                    distances[v] = distances[u] + edge.weight
                    parent[v] = u
                    relaxed_any = True
                    
                    states.append(AlgoState(
                        distances=dict(distances),
                        highlighted_edges={edge.id},
                        message=f"Relaxed edge {graph.get_node(u).label} -> {graph.get_node(v).label}: new dist = {distances[v]} (was {old_dist})",
                        detail_text=format_dist_text()
                    ))
                    
                if not edge.directed and distances[v] != float('inf') and distances[v] + edge.weight < distances[u]:
                    old_dist = distances[u]
                    distances[u] = distances[v] + edge.weight
                    parent[u] = v
                    relaxed_any = True
                    
                    states.append(AlgoState(
                        distances=dict(distances),
                        highlighted_edges={edge.id},
                        message=f"Relaxed edge {graph.get_node(v).label} -> {graph.get_node(u).label}: new dist = {distances[u]} (was {old_dist})",
                        detail_text=format_dist_text()
                      ))
                      
            if not relaxed_any:
                states.append(AlgoState(
                    distances=dict(distances),
                    message=f"No edges relaxed in iteration {i + 1}. Algorithm converged early.",
                    detail_text=format_dist_text()
                ))
                break

        has_negative_cycle = False
        cycle_edges = set()
        for edge in edges_list:
            u = edge.u
            v = edge.v
            if distances[u] != float('inf') and distances[u] + edge.weight < distances[v]:
                has_negative_cycle = True
                cycle_edges.add(edge.id)
            if not edge.directed and distances[v] != float('inf') and distances[v] + edge.weight < distances[u]:
                has_negative_cycle = True
                cycle_edges.add(edge.id)

        if has_negative_cycle:
            states.append(AlgoState(
                distances=dict(distances),
                highlighted_edges=cycle_edges,
                message="Negative cycle detected! Infinite negative relaxation possible.",
                detail_text="Graph contains negative weight cycle."
            ))
        else:
            final_edges = set()
            for nid in distances:
                p = parent.get(nid)
                if p:
                    for e in graph.edges_between(nid, p):
                        final_edges.add(e.id)
                        
            states.append(AlgoState(
                distances=dict(distances),
                highlighted_edges=final_edges,
                message="Bellman-Ford Complete (No negative cycles detected)",
                detail_text=format_dist_text()
            ))

        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
