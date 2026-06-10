from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class TopologicalSort(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Topological Sort"

    @property
    def description(self) -> str:
        return "Finds a linear ordering of vertices such that for every directed edge u -> v, u comes before v. Detects cycles."

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = list(graph.nodes())
        
        in_degrees = {n.id: 0 for n in nodes_list}
        for edge in graph.edges():
            if edge.directed:
                in_degrees[edge.v] += 1
            else:
                in_degrees[edge.v] += 1
                in_degrees[edge.u] += 1
                
        def format_state_text(queue, order):
            lines = ["In-degrees:"]
            for nid, deg in sorted(in_degrees.items(), key=lambda x: graph.get_node(x[0]).label if graph.get_node(x[0]) else ""):
                node = graph.get_node(nid)
                if node:
                    lines.append(f"  {node.label}: {deg}")
            lines.append(f"Queue: {[graph.get_node(nid).label for nid in queue]}")
            lines.append(f"Order: {[graph.get_node(nid).label for nid in order]}")
            return "\n".join(lines)

        queue = [nid for nid, deg in in_degrees.items() if deg == 0]
        queue.sort(key=lambda nid: graph.get_node(nid).label if graph.get_node(nid) else "")
        
        order = []
        
        states.append(AlgoState(
            frontier=set(queue),
            message="Calculate initial in-degrees and queue nodes with in-degree 0",
            detail_text=format_state_text(queue, order)
        ))
        
        while queue:
            u = queue.pop(0)
            order.append(u)
            
            states.append(AlgoState(
                visited=set(order),
                frontier=set(queue),
                message=f"Added node '{graph.get_node(u).label}' to topological order",
                detail_text=format_state_text(queue, order)
            ))
            
            for edge in graph.edges_of(u):
                if edge.directed:
                    if edge.u == u:
                        neighbor = edge.v
                    else:
                        continue
                else:
                    neighbor = edge.v if edge.u == u else edge.u
                    
                if neighbor not in order:
                    in_degrees[neighbor] = max(0, in_degrees[neighbor] - 1)
                    
                    states.append(AlgoState(
                        visited=set(order),
                        frontier=set(queue),
                        highlighted_edges={edge.id},
                        message=f"Decreased in-degree of neighbor '{graph.get_node(neighbor).label}'",
                        detail_text=format_state_text(queue, order)
                    ))
                    
                    if in_degrees[neighbor] == 0 and neighbor not in queue:
                        queue.append(neighbor)
                        queue.sort(key=lambda nid: graph.get_node(nid).label if graph.get_node(nid) else "")
                        
                        states.append(AlgoState(
                            visited=set(order),
                            frontier=set(queue),
                            message=f"Node '{graph.get_node(neighbor).label}' has in-degree 0; added to queue",
                            detail_text=format_state_text(queue, order)
                        ))

        if len(order) < len(nodes_list):
            cycle_nodes = set(n.id for n in nodes_list if n.id not in order)
            states.append(AlgoState(
                visited=set(order),
                frontier=cycle_nodes,
                message="Cycle detected! Graph is not a DAG. Topological sort impossible.",
                detail_text="Remaining nodes have dependencies forming a cycle."
            ))
        else:
            states.append(AlgoState(
                visited=set(order),
                message="Topological Sort Complete",
                detail_text=format_state_text([], order)
            ))
            
        total = len(states)
        for idx, state in enumerate(states):
            state.step_index = idx + 1
            state.total_steps = total
            
        return states
