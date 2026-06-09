"""
Tarjan's algorithm for finding Strongly Connected Components (SCC).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

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
