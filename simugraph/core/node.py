"""
Node dataclass — represents a single vertex in the graph.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import uuid


@dataclass
class Node:
    """A vertex in the graph with position, label, and visual properties."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    x: float = 0.0
    y: float = 0.0
    color: tuple[int, int, int] = (60, 130, 220)
    radius: int = 22
    pinned: bool = False      # when True, spring layout ignores this node
    selected: bool = False
    weight: float = 0.0
    shape: str = "circle"      # "circle", "square", "hexagon"

    def __post_init__(self) -> None:
        # Ensure color is always a plain tuple (not list)
        self.color = tuple(self.color)

    def distance_to(self, other: Node) -> float:
        """Euclidean distance between two nodes (world coordinates)."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return self.id == other.id
        return NotImplemented
