"""
Algorithm to find bridges and articulation points (cut vertices) in a graph.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph


def find_bridges_and_articulation_points(graph: Graph) -> tuple[set[str], set[str]]:
    """
    Computes cut vertices (articulation points) and bridges (cut edges).
    Treats directed edges as undirected.
    Returns:
        A tuple (articulation_points, bridges) containing sets of IDs.
    """
    nodes_list = graph.nodes()
    # Adjacency list: mapping node_id -> list of (neighbor_id, edge_id)
    adj: dict[str, list[tuple[str, str]]] = {n.id: [] for n in nodes_list}
    for e in graph.edges():
        if e.u in adj and e.v in adj:
            adj[e.u].append((e.v, e.id))
            if e.u != e.v:  # Avoid self-loop duplicates
                adj[e.v].append((e.u, e.id))

    visited = {n.id: False for n in nodes_list}
    disc = {n.id: 0 for n in nodes_list}
    low = {n.id: 0 for n in nodes_list}
    parent: dict[str, str | None] = {n.id: None for n in nodes_list}
    
    articulation_points: set[str] = set()
    bridges: set[str] = set()
    time = 0

    def dfs(u: str) -> None:
        nonlocal time
        visited[u] = True
        disc[u] = low[u] = time
        time += 1
        children = 0
        is_ap = False

        for v, edge_id in adj[u]:
            if not visited[v]:
                children += 1
                parent[v] = u
                dfs(v)

                low[u] = min(low[u], low[v])

                # Articulation Point criteria:
                # 1. Root node with >= 2 children
                if parent[u] is None and children > 1:
                    is_ap = True
                # 2. Non-root node where low[v] >= disc[u]
                if parent[u] is not None and low[v] >= disc[u]:
                    is_ap = True
                
                # Bridge criteria:
                if low[v] > disc[u]:
                    # Make sure we don't count parallel edges as bridges
                    # (if there are multiple edges between u and v, neither is a bridge)
                    edges_between = graph.edges_between(u, v)
                    if len(edges_between) == 1:
                        bridges.add(edge_id)
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

        if is_ap:
            articulation_points.add(u)

    for node in nodes_list:
        if not visited[node.id]:
            dfs(node.id)

    return articulation_points, bridges
