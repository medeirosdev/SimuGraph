"""
Fruchterman-Reingold force-directed layout implementation.
"""
from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph


def run_fruchterman_reingold_step(
    graph: Graph,
    k: float = 120.0,
    temp: float = 20.0,
) -> None:
    """
    Runs a single iteration of the Fruchterman-Reingold layout algorithm on the graph.
    Modifies node positions in-place, respecting node.pinned status.
    """
    nodes = graph.nodes()
    if len(nodes) < 2:
        return

    # Initialize displacements
    disp = {node.id: [0.0, 0.0] for node in nodes}

    # 1. Repulsive forces between all pairs
    for i in range(len(nodes)):
        node_u = nodes[i]
        for j in range(i + 1, len(nodes)):
            node_v = nodes[j]
            dx = node_u.x - node_v.x
            dy = node_u.y - node_v.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                # Add tiny random perturbation to split overlapping nodes
                dx = 0.5
                dy = 0.5
                dist = 0.707

            # f_r = (k^2) / dist
            fr = (k ** 2) / dist
            fx = (dx / dist) * fr
            fy = (dy / dist) * fr

            disp[node_u.id][0] += fx
            disp[node_u.id][1] += fy
            disp[node_v.id][0] -= fx
            disp[node_v.id][1] -= fy

    # 2. Attractive forces along edges
    for edge in graph.edges():
        u_node = graph.get_node(edge.u)
        v_node = graph.get_node(edge.v)
        if u_node and v_node and edge.u != edge.v:
            dx = u_node.x - v_node.x
            dy = u_node.y - v_node.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue

            # f_a = (dist^2) / k
            fa = (dist ** 2) / k
            fx = (dx / dist) * fa
            fy = (dy / dist) * fa

            disp[edge.u][0] -= fx
            disp[edge.u][1] -= fy
            disp[edge.v][0] += fx
            disp[edge.v][1] += fy

    # 3. Apply displacement limited by temperature
    for node in nodes:
        if node.pinned:
            continue

        dx = disp[node.id][0]
        dy = disp[node.id][1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue

        # Limit displacement to max temperature
        limited_dist = min(dist, temp)
        node.x += (dx / dist) * limited_dist
        node.y += (dy / dist) * limited_dist
