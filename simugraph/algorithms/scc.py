"""
Tarjan's algorithm for finding Strongly Connected Components (SCC).
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

if TYPE_CHECKING:
    from simugraph.core.graph import Graph


def find_sccs(graph: Graph) -> list[list[str]]:
    """
    Computes SCCs using Tarjan's strongly connected components algorithm.
    Treats undirected edges as bidirectional connections.
    Returns:
        A list of strongly connected components (lists of node IDs).
    """
    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: dict[str, bool] = {}
    stack: list[str] = []
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True

        for neighbor in graph.neighbors(v):
            w = neighbor.id
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            component = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                component.append(w)
                if w == v:
                    break
            sccs.append(component)

    for node in graph.nodes():
        if node.id not in indices:
            strongconnect(node.id)

    return sccs


class TarjanSCC(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Tarjan's SCC"

    @property
    def description(self) -> str:
        return "Finds Strongly Connected Components using Tarjan's algorithm"

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = sorted(list(graph.nodes()), key=lambda n: n.label)
        if not nodes_list:
            return [AlgoState(message="Empty graph.", step_index=1, total_steps=1)]

        # Tarjan state variables
        index = 0
        indices: dict[str, int] = {}
        lowlink: dict[str, int] = {}
        on_stack: dict[str, bool] = {}
        stack: list[str] = []
        sccs: list[set[str]] = []

        def get_detail_text(curr_node_label: str) -> str:
            lines = []
            lines.append(f"Current node: {curr_node_label}")
            stack_labels = [graph.get_node(nid).label for nid in stack if graph.get_node(nid)]
            lines.append(f"Stack: {', '.join(stack_labels)}\n")
            lines.append("Node statuses:")
            lines.append(f"{'Node':<6} {'Index':<8} {'Lowlink':<8} {'On Stack':<10}")
            for n in nodes_list:
                idx_str = str(indices[n.id]) if n.id in indices else "-"
                low_str = str(lowlink[n.id]) if n.id in lowlink else "-"
                os_str = "Yes" if on_stack.get(n.id, False) else "No"
                lines.append(f"{n.label:<6} {idx_str:<8} {low_str:<8} {os_str:<10}")
            
            if sccs:
                lines.append("\nStrongly Connected Components found:")
                for idx, comp in enumerate(sccs):
                    comp_labels = sorted([graph.get_node(nid).label for nid in comp if graph.get_node(nid)])
                    lines.append(f" SCC {idx+1}: {{{', '.join(comp_labels)}}}")
            return "\n".join(lines)

        def strongconnect(v: str) -> None:
            nonlocal index
            v_node = graph.get_node(v)
            if not v_node: return

            indices[v] = index
            lowlink[v] = index
            index += 1
            stack.append(v)
            on_stack[v] = True

            states.append(AlgoState(
                visited=set(indices.keys()),
                frontier=set(stack),
                scc_groups=list(sccs),
                message=f"Visited {v_node.label}: index={indices[v]}, lowlink={lowlink[v]}.",
                detail_text=get_detail_text(v_node.label)
            ))

            for neighbor in graph.neighbors(v):
                w = neighbor.id
                if w not in indices:
                    # Recursive call
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                    states.append(AlgoState(
                        visited=set(indices.keys()),
                        frontier=set(stack),
                        scc_groups=list(sccs),
                        message=f"Backtracked from {neighbor.label} to {v_node.label}: updated lowlink={lowlink[v]}.",
                        detail_text=get_detail_text(v_node.label)
                    ))
                elif on_stack.get(w, False):
                    lowlink[v] = min(lowlink[v], indices[w])
                    states.append(AlgoState(
                        visited=set(indices.keys()),
                        frontier=set(stack),
                        scc_groups=list(sccs),
                        message=f"Neighbor {neighbor.label} is on stack: updated lowlink of {v_node.label} to {lowlink[v]}.",
                        detail_text=get_detail_text(v_node.label)
                    ))

            if lowlink[v] == indices[v]:
                component = set()
                popped_labels = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.add(w)
                    w_node = graph.get_node(w)
                    if w_node:
                        popped_labels.append(w_node.label)
                    if w == v:
                        break
                sccs.append(component)
                states.append(AlgoState(
                    visited=set(indices.keys()),
                    frontier=set(stack),
                    scc_groups=list(sccs),
                    message=f"Found SCC: {{{', '.join(popped_labels)}}}.",
                    detail_text=get_detail_text(v_node.label)
                ))

        for node in nodes_list:
            if node.id not in indices:
                strongconnect(node.id)

        # Final state
        states.append(AlgoState(
            visited=set(indices.keys()),
            scc_groups=list(sccs),
            message="Tarjan's strongly connected components algorithm complete.",
            detail_text=get_detail_text("None")
        ))

        # Update steps
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
