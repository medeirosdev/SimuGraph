"""
Algorithm to find bridges and articulation points (cut vertices) in a graph.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

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


class BridgesAndAPs(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Bridges & APs"

    @property
    def description(self) -> str:
        return "Finds bridges and articulation points (cut vertices)"

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = sorted(list(graph.nodes()), key=lambda n: n.label)
        if not nodes_list:
            return [AlgoState(message="Empty graph.", step_index=1, total_steps=1)]

        adj: dict[str, list[tuple[str, str]]] = {n.id: [] for n in nodes_list}
        for e in graph.edges():
            if e.u in adj and e.v in adj:
                adj[e.u].append((e.v, e.id))
                if e.u != e.v:
                    adj[e.v].append((e.u, e.id))

        visited_flags = {n.id: False for n in nodes_list}
        disc = {n.id: 0 for n in nodes_list}
        low = {n.id: 0 for n in nodes_list}
        parent = {n.id: None for n in nodes_list}
        
        articulation_points = set()
        bridges = set()
        time = 0
        dfs_stack = []

        def get_detail_text(curr_node_label: str) -> str:
            lines = []
            lines.append(f"Current DFS node: {curr_node_label}")
            stack_labels = [graph.get_node(nid).label for nid in dfs_stack if graph.get_node(nid)]
            lines.append(f"DFS Path: {' -> '.join(stack_labels)}\n")
            lines.append("Node states:")
            lines.append(f"{'Node':<6} {'Visited':<8} {'Disc':<6} {'Low':<6} {'Parent':<8}")
            for n in nodes_list:
                v_str = "Yes" if visited_flags[n.id] else "No"
                disc_str = str(disc[n.id]) if visited_flags[n.id] else "-"
                low_str = str(low[n.id]) if visited_flags[n.id] else "-"
                p_node = graph.get_node(parent[n.id]) if parent[n.id] else None
                p_str = p_node.label if p_node else "-"
                lines.append(f"{n.label:<6} {v_str:<8} {disc_str:<6} {low_str:<6} {p_str:<8}")
            
            if articulation_points:
                ap_labels = sorted([graph.get_node(nid).label for nid in articulation_points if graph.get_node(nid)])
                lines.append(f"\nArticulation Points: {{{', '.join(ap_labels)}}}")
            if bridges:
                br_edges = []
                for bid in bridges:
                    edge = None
                    for e in graph.edges():
                        if e.id == bid:
                            edge = e
                            break
                    if edge:
                        u_lbl = graph.get_node(edge.u).label
                        v_lbl = graph.get_node(edge.v).label
                        br_edges.append(f"({u_lbl}-{v_lbl})")
                lines.append(f"Bridges: {', '.join(sorted(br_edges))}")
            return "\n".join(lines)

        def dfs(u: str) -> None:
            nonlocal time
            u_node = graph.get_node(u)
            if not u_node: return

            visited_flags[u] = True
            disc[u] = low[u] = time
            time += 1
            children = 0
            is_ap = False
            dfs_stack.append(u)

            states.append(AlgoState(
                visited={nid for nid, v in visited_flags.items() if v},
                frontier=set(dfs_stack),
                message=f"DFS visit {u_node.label}: discovery time={disc[u]}.",
                detail_text=get_detail_text(u_node.label)
            ))
            states[-1].bridges = bridges.copy()
            states[-1].articulation_points = articulation_points.copy()

            for v, edge_id in adj[u]:
                v_node = graph.get_node(v)
                if not v_node: continue

                if not visited_flags[v]:
                    children += 1
                    parent[v] = u
                    dfs(v)

                    low[u] = min(low[u], low[v])
                    
                    # Check AP conditions
                    if parent[u] is None and children > 1:
                        is_ap = True
                    if parent[u] is not None and low[v] >= disc[u]:
                        is_ap = True

                    # Check Bridge conditions
                    if low[v] > disc[u]:
                        edges_between = graph.edges_between(u, v)
                        if len(edges_between) == 1:
                            bridges.add(edge_id)

                    states.append(AlgoState(
                        visited={nid for nid, v in visited_flags.items() if v},
                        frontier=set(dfs_stack),
                        message=f"Backtracked to {u_node.label} from {v_node.label}: updated lowlink={low[u]}.",
                        detail_text=get_detail_text(u_node.label)
                    ))
                    states[-1].bridges = bridges.copy()
                    states[-1].articulation_points = articulation_points.copy()

                elif v != parent[u]:
                    low[u] = min(low[u], disc[v])
                    states.append(AlgoState(
                        visited={nid for nid, v in visited_flags.items() if v},
                        frontier=set(dfs_stack),
                        message=f"Back-edge from {u_node.label} to {v_node.label}: updated lowlink={low[u]}.",
                        detail_text=get_detail_text(u_node.label)
                    ))
                    states[-1].bridges = bridges.copy()
                    states[-1].articulation_points = articulation_points.copy()

            if is_ap:
                articulation_points.add(u)
                states.append(AlgoState(
                    visited={nid for nid, v in visited_flags.items() if v},
                    frontier=set(dfs_stack),
                    message=f"Identified {u_node.label} as an Articulation Point.",
                    detail_text=get_detail_text(u_node.label)
                ))
                states[-1].bridges = bridges.copy()
                states[-1].articulation_points = articulation_points.copy()

            dfs_stack.pop()

        for node in nodes_list:
            if not visited_flags[node.id]:
                dfs(node.id)

        # Final state
        states.append(AlgoState(
            visited={nid for nid, v in visited_flags.items() if v},
            frontier=set(),
            message="Bridge and Articulation Point detection complete.",
            detail_text=get_detail_text("None")
        ))
        states[-1].bridges = bridges.copy()
        states[-1].articulation_points = articulation_points.copy()

        # Update steps
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
