from __future__ import annotations
from simugraph.algorithms.base import StepAlgorithm, AlgoState
from simugraph.core.graph import Graph

class ExamplePluginAlgorithm(StepAlgorithm):
    """
    An example plugin algorithm that demonstrates how to implement a custom
    algorithm in SimuGraph. 
    
    This algorithm inspects each node and highlights those with an odd degree.
    """

    @property
    def name(self) -> str:
        return "Odd Degree Highlighter"

    @property
    def description(self) -> str:
        return "Plugin: Highlights all nodes with an odd number of connections (degree)."

    @property
    def requires_source(self) -> bool:
        # This plugin scans the whole graph, so a starting source node is not required
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states = []
        nodes = list(graph.nodes())
        
        # Step 0: Initial State
        initial_state = AlgoState(
            visited=set(),
            frontier=set(),
            message="Initializing Odd Degree Highlighter plugin...",
            step_index=0,
            total_steps=len(nodes) + 1,
            detail_text="Analyzing connections for all nodes in the graph."
        )
        states.append(initial_state)
        
        odd_nodes = set()
        
        # Inspect nodes one by one
        for idx, node in enumerate(nodes):
            degree = graph.degree(node.id)
            is_odd = (degree % 2 != 0)
            
            # The Odd nodes found so far will be colored as 'visited' (green)
            current_visited = set(odd_nodes)
            # The node currently being inspected is the 'frontier' (orange/yellow)
            current_frontier = {node.id}
            
            msg = f"Checking Node {node.label}: degree is {degree} ({'Odd' if is_odd else 'Even'})"
            detail = f"Node ID: {node.id}\nDegree: {degree}"
            
            if is_odd:
                odd_nodes.add(node.id)
                msg += " -> Highlights as Odd!"
            
            state = AlgoState(
                visited=current_visited,
                frontier=current_frontier,
                message=msg,
                step_index=idx + 1,
                total_steps=len(nodes) + 1,
                detail_text=detail
            )
            states.append(state)
            
        # Final Step: Show overall results
        final_state = AlgoState(
            visited=odd_nodes,
            frontier=set(),
            message=f"Completed! Found {len(odd_nodes)} nodes with odd degrees.",
            step_index=len(nodes) + 1,
            total_steps=len(nodes) + 1,
            detail_text=f"Odd degree nodes: {', '.join(graph.get_node(nid).label for nid in odd_nodes)}" if odd_nodes else "No odd degree nodes found."
        )
        states.append(final_state)
        
        return states
