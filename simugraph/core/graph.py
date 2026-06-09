"""
Graph model — central data structure holding nodes and edges.
"""

from __future__ import annotations
from typing import Iterator
from .node import Node
from .edge import Edge


class Graph:
    """
    Undirected / directed multigraph model.

    Nodes and edges are stored in insertion-order dicts keyed by their UUID.
    All mutation goes through add_* / remove_* so higher-level code
    (commands, properties, renderers) has a single source of truth.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, Edge] = {}

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """Insert a node. No-op if the id already exists."""
        if node.id not in self._nodes:
            self._nodes[node.id] = node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all edges that touch it."""
        self._nodes.pop(node_id, None)
        to_delete = [eid for eid, e in self._edges.items() if e.connects(node_id)]
        for eid in to_delete:
            del self._edges[eid]

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def nodes(self) -> list[Node]:
        return list(self._nodes.values())

    def node_count(self) -> int:
        return len(self._nodes)

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    def add_edge(self, edge: Edge) -> None:
        """Insert an edge. Both endpoint ids must already exist."""
        if edge.u not in self._nodes or edge.v not in self._nodes:
            raise ValueError(
                f"Cannot add edge: node(s) {edge.u!r}/{edge.v!r} not in graph."
            )
        if edge.id not in self._edges:
            self._edges[edge.id] = edge

    def remove_edge(self, edge_id: str) -> None:
        self._edges.pop(edge_id, None)

    def get_edge(self, edge_id: str) -> Edge | None:
        return self._edges.get(edge_id)

    def edges(self) -> list[Edge]:
        return list(self._edges.values())

    def edge_count(self) -> int:
        return len(self._edges)

    # ------------------------------------------------------------------
    # Adjacency helpers
    # ------------------------------------------------------------------

    def neighbors(self, node_id: str) -> list[Node]:
        """
        All nodes directly reachable from node_id.
        For directed graphs this follows edge direction (u → v).
        For undirected graphs both endpoints are treated symmetrically.
        """
        result: list[Node] = []
        for e in self._edges.values():
            if e.directed:
                if e.u == node_id and e.v in self._nodes:
                    result.append(self._nodes[e.v])
            else:
                if e.u == node_id and e.v in self._nodes:
                    result.append(self._nodes[e.v])
                elif e.v == node_id and e.u in self._nodes:
                    result.append(self._nodes[e.u])
        return result

    def edges_of(self, node_id: str) -> list[Edge]:
        """All edges that touch node_id."""
        return [e for e in self._edges.values() if e.connects(node_id)]

    def degree(self, node_id: str) -> int:
        """Number of edges incident to node_id (self-loops count twice)."""
        count = 0
        for e in self._edges.values():
            if e.is_self_loop() and e.u == node_id:
                count += 2
            elif e.connects(node_id):
                count += 1
        return count

    def edges_between(self, u_id: str, v_id: str) -> list[Edge]:
        """All edges between two specific nodes (parallel edges included)."""
        return [
            e for e in self._edges.values()
            if (e.u == u_id and e.v == v_id)
            or (not e.directed and e.u == v_id and e.v == u_id)
        ]

    def has_edge(self, u_id: str, v_id: str) -> bool:
        return bool(self.edges_between(u_id, v_id))

    # ------------------------------------------------------------------
    # Graph-level properties (cheap checks)
    # ------------------------------------------------------------------

    def is_directed(self) -> bool:
        """True if ANY edge in the graph is directed."""
        return any(e.directed for e in self._edges.values())

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------

    def iter_adjacency(self) -> Iterator[tuple[Node, list[Node]]]:
        """Yields (node, neighbor_list) for every node."""
        for node in self._nodes.values():
            yield node, self.neighbors(node.id)

    def adjacency_dict(self) -> dict[str, list[str]]:
        """Returns {node_id: [neighbor_id, ...]} for all nodes."""
        return {nid: [n.id for n in self.neighbors(nid)] for nid in self._nodes}

    def __repr__(self) -> str:
        return (
            f"Graph(nodes={self.node_count()}, edges={self.edge_count()}, "
            f"directed={self.is_directed()})"
        )
