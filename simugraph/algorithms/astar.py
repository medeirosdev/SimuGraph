from __future__ import annotations
import math
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class AStar(StepAlgorithm):
    @property
    def name(self) -> str:
        return "A*"

    @property
    def description(self) -> str:
        return "A* Shortest Path with Euclidean heuristic"

    @property
    def requires_source(self) -> bool:
        return True

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        if not source or not graph.get_node(source):
            return [AlgoState(message="Invalid source node.", step_index=1, total_steps=1)]

        # Determine target node
        # 1. Look for a selected node that is not the source
        target: str | None = None
        for n in graph.nodes():
            if n.selected and n.id != source:
                target = n.id
                break
        
        # 2. If none, pick alphabetically last node that is not the source
        if not target:
            nodes_sorted = sorted(list(graph.nodes()), key=lambda n: n.label)
            for n in reversed(nodes_sorted):
                if n.id != source:
                    target = n.id
                    break
        
        # 3. Fallback to source
        if not target:
            target = source

        src_node = graph.get_node(source)
        tgt_node = graph.get_node(target)
        
        # Heuristic function: Euclidean distance
        def h(node_id: str) -> float:
            n1 = graph.get_node(node_id)
            if not n1 or not tgt_node:
                return 0.0
            return math.hypot(n1.x - tgt_node.x, n1.y - tgt_node.y)

        # A* initialization
        # g_score[node] is cost from source to node
        g_score = {node.id: float('inf') for node in graph.nodes()}
        g_score[source] = 0.0

        # f_score[node] = g_score[node] + h(node)
        f_score = {node.id: float('inf') for node in graph.nodes()}
        f_score[source] = h(source)

        parent = {}
        open_set = {source}
        closed_set = set()

        def get_detail_text() -> str:
            lines = []
            lines.append(f"Source: {src_node.label if src_node else ''}")
            lines.append(f"Target: {tgt_node.label if tgt_node else ''}\n")
            lines.append("Node details:")
            lines.append(f"{'Node':<6} {'g (cost)':<10} {'h (heur)':<10} {'f (total)':<10} {'Status':<10}")
            for n in sorted(list(graph.nodes()), key=lambda x: x.label):
                status = "Unvisited"
                if n.id in closed_set:
                    status = "Visited"
                elif n.id in open_set:
                    status = "Frontier"
                
                g_str = f"{g_score[n.id]:.2f}" if g_score[n.id] != float('inf') else "inf"
                h_val = h(n.id)
                f_str = f"{f_score[n.id]:.2f}" if f_score[n.id] != float('inf') else "inf"
                lines.append(f"{n.label:<6} {g_str:<10} {h_val:<10.2f} {f_str:<10} {status:<10}")
            return "\n".join(lines)

        states.append(AlgoState(
            visited=set(),
            frontier=open_set.copy(),
            distances={k: v for k, v in g_score.items() if v != float('inf')},
            message=f"Starting A* search from {src_node.label} to {tgt_node.label}.",
            detail_text=get_detail_text()
        ))

        found = False
        while open_set:
            # Pick node in open_set with minimum f_score
            current = min(open_set, key=lambda node: f_score[node])
            curr_node = graph.get_node(current)

            if current == target:
                found = True
                break

            open_set.remove(current)
            closed_set.add(current)

            # Record step popping current node
            states.append(AlgoState(
                visited=closed_set.copy(),
                frontier=open_set.copy(),
                distances={k: v for k, v in g_score.items() if v != float('inf')},
                message=f"Expanding node {curr_node.label if curr_node else ''} (f = {f_score[current]:.2f}).",
                detail_text=get_detail_text()
            ))

            # Relax neighbors
            neighbors = graph.neighbors(current)
            any_update = False
            updated_nodes = []
            
            for neighbor in neighbors:
                neighbor_id = neighbor.id
                if neighbor_id in closed_set:
                    continue

                # Edge weight
                weight = 1.0
                edges = graph.edges_between(current, neighbor_id)
                if edges:
                    weight = min(e.weight for e in edges)

                tentative_g = g_score[current] + weight
                if tentative_g < g_score[neighbor_id]:
                    parent[neighbor_id] = current
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + h(neighbor_id)
                    open_set.add(neighbor_id)
                    any_update = True
                    updated_nodes.append(neighbor.label)

            if any_update:
                states.append(AlgoState(
                    visited=closed_set.copy(),
                    frontier=open_set.copy(),
                    distances={k: v for k, v in g_score.items() if v != float('inf')},
                    message=f"Relaxing neighbors of {curr_node.label if curr_node else ''}: updated {', '.join(updated_nodes)}.",
                    detail_text=get_detail_text()
                ))

        if found:
            # Reconstruct path
            path = []
            curr = target
            while curr in parent:
                path.append(curr)
                curr = parent[curr]
            path.append(source)
            path.reverse()

            # Find highlighted edges
            highlighted_edges = set()
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edges = graph.edges_between(u, v)
                if edges:
                    best_edge = min(edges, key=lambda e: e.weight)
                    highlighted_edges.add(best_edge.id)

            states.append(AlgoState(
                visited=closed_set.copy(),
                frontier=open_set.copy(),
                path=path,
                highlighted_edges=highlighted_edges,
                distances={k: v for k, v in g_score.items() if v != float('inf')},
                message=f"A* shortest path found! Cost: {g_score[target]:.2f}",
                detail_text=get_detail_text()
            ))
        else:
            states.append(AlgoState(
                visited=closed_set.copy(),
                frontier=open_set.copy(),
                distances={k: v for k, v in g_score.items() if v != float('inf')},
                message="A* complete. No path from source to target exists.",
                detail_text=get_detail_text()
            ))

        # Update step indexes
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
