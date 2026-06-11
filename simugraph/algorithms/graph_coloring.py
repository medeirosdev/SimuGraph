from __future__ import annotations
from typing import TYPE_CHECKING
from simugraph.algorithms.base import StepAlgorithm, AlgoState

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class GraphColoring(StepAlgorithm):
    @property
    def name(self) -> str:
        return "Graph Coloring"

    @property
    def description(self) -> str:
        return "Greedy graph coloring using Welch-Powell heuristic"

    @property
    def requires_source(self) -> bool:
        return False

    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        states: list[AlgoState] = []
        nodes_list = sorted(list(graph.nodes()), key=lambda n: (-graph.degree(n.id), n.label))
        if not nodes_list:
            return [AlgoState(message="Empty graph.", step_index=1, total_steps=1)]

        colors = {} # node.id -> color index (0, 1, 2...)

        def get_detail_text(curr_node_id: str | None) -> str:
            lines = []
            if curr_node_id:
                curr_node = graph.get_node(curr_node_id)
                lines.append(f"Coloring Node: {curr_node.label if curr_node else ''}")
            else:
                lines.append("Coloring process complete.")
            
            used_colors = set(colors.values())
            chromatic_estimate = len(used_colors)
            lines.append(f"Estimated Chromatic Number: {chromatic_estimate}\n")
            lines.append("Node Color Allocations:")
            lines.append(f"{'Node':<6} {'Degree':<8} {'Color Index':<12} {'Color Name':<12}")
            color_names = ["Blue", "Green", "Orange", "Pink", "Purple", "Yellow", "Cyan", "Red"]
            
            # Sort by label to display clean table
            for n in sorted(list(graph.nodes()), key=lambda x: x.label):
                deg = graph.degree(n.id)
                col_idx = colors.get(n.id, None)
                col_idx_str = str(col_idx) if col_idx is not None else "-"
                col_name = color_names[col_idx % len(color_names)] if col_idx is not None else "-"
                lines.append(f"{n.label:<6} {deg:<8} {col_idx_str:<12} {col_name:<12}")
            return "\n".join(lines)

        states.append(AlgoState(
            colors=colors.copy(),
            message="Initializing Welch-Powell greedy graph coloring (nodes sorted by degree descending).",
            detail_text=get_detail_text(None)
        ))

        for node in nodes_list:
            # Find colors used by neighbors
            neighbor_colors = set()
            for neighbor in graph.neighbors(node.id):
                if neighbor.id in colors:
                    neighbor_colors.add(colors[neighbor.id])

            # Find the lowest unused color
            color = 0
            while color in neighbor_colors:
                color += 1

            colors[node.id] = color

            states.append(AlgoState(
                visited={node.id},
                colors=colors.copy(),
                message=f"Coloring node {node.label} with color index {color}.",
                detail_text=get_detail_text(node.id)
            ))

        # Final state
        used_colors = set(colors.values())
        states.append(AlgoState(
            colors=colors.copy(),
            message=f"Graph coloring complete. Estimated Chromatic Number: {len(used_colors)}.",
            detail_text=get_detail_text(None)
        ))

        # Update step indexes
        total = len(states)
        for idx, st in enumerate(states):
            st.step_index = idx + 1
            st.total_steps = total

        return states
