"""
Edge dataclass — represents a connection between two nodes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import uuid


@dataclass
class Edge:
    """A connection between two nodes, optionally directed and weighted."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    u: str = ""             # source node id
    v: str = ""             # target node id
    weight: float = 1.0
    directed: bool = False
    color: tuple[int, int, int] = (150, 155, 185)
    selected: bool = False

    def __post_init__(self) -> None:
        self.color = tuple(self.color)

    def connects(self, node_id: str) -> bool:
        """Returns True if this edge touches the given node id."""
        return self.u == node_id or self.v == node_id

    def other(self, node_id: str) -> str:
        """Given one endpoint id, return the other."""
        if self.u == node_id:
            return self.v
        if self.v == node_id:
            return self.u
        raise ValueError(f"Node {node_id!r} is not an endpoint of edge {self.id!r}")

    def is_self_loop(self) -> bool:
        return self.u == self.v

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Edge):
            return self.id == other.id
        return NotImplemented
