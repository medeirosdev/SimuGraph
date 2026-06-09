"""
Command pattern for undo/redo functionality in SimuGraph.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph
    from simugraph.core.node import Node
    from simugraph.core.edge import Edge


class Command(ABC):
    """Abstract base class for all undoable commands."""

    @abstractmethod
    def execute(self, graph: Graph) -> None:
        """Apply the command to the graph."""
        pass

    @abstractmethod
    def undo(self, graph: Graph) -> None:
        """Reverse the command on the graph."""
        pass


class AddNodeCommand(Command):
    def __init__(self, node: Node) -> None:
        self.node = node

    def execute(self, graph: Graph) -> None:
        graph.add_node(self.node)

    def undo(self, graph: Graph) -> None:
        graph.remove_node(self.node.id)


class RemoveNodeCommand(Command):
    def __init__(self, node: Node, related_edges: list[Edge]) -> None:
        self.node = node
        self.related_edges = related_edges

    def execute(self, graph: Graph) -> None:
        graph.remove_node(self.node.id)

    def undo(self, graph: Graph) -> None:
        graph.add_node(self.node)
        for edge in self.related_edges:
            graph.add_edge(edge)


class AddEdgeCommand(Command):
    def __init__(self, edge: Edge) -> None:
        self.edge = edge

    def execute(self, graph: Graph) -> None:
        graph.add_edge(self.edge)

    def undo(self, graph: Graph) -> None:
        graph.remove_edge(self.edge.id)


class RemoveEdgeCommand(Command):
    def __init__(self, edge: Edge) -> None:
        self.edge = edge

    def execute(self, graph: Graph) -> None:
        graph.remove_edge(self.edge.id)

    def undo(self, graph: Graph) -> None:
        graph.add_edge(self.edge)


class MoveNodeCommand(Command):
    def __init__(self, node_id: str, old_pos: tuple[float, float], new_pos: tuple[float, float]) -> None:
        self.node_id = node_id
        self.old_pos = old_pos
        self.new_pos = new_pos

    def execute(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.x, node.y = self.new_pos

    def undo(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.x, node.y = self.old_pos


class RenameNodeCommand(Command):
    def __init__(self, node_id: str, old_label: str, new_label: str) -> None:
        self.node_id = node_id
        self.old_label = old_label
        self.new_label = new_label

    def execute(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.label = self.new_label

    def undo(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.label = self.old_label


class ChangeNodeColorCommand(Command):
    def __init__(self, node_id: str, old_color: tuple[int, int, int], new_color: tuple[int, int, int]) -> None:
        self.node_id = node_id
        self.old_color = old_color
        self.new_color = new_color

    def execute(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.color = self.new_color

    def undo(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.color = self.old_color


class ToggleNodePinCommand(Command):
    def __init__(self, node_id: str, old_pinned: bool, new_pinned: bool) -> None:
        self.node_id = node_id
        self.old_pinned = old_pinned
        self.new_pinned = new_pinned

    def execute(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.pinned = self.new_pinned

    def undo(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.pinned = self.old_pinned


class ColorComponentsCommand(Command):
    def __init__(self, color_map: dict[str, tuple[int, int, int]]) -> None:
        self.color_map = color_map
        self.old_colors: dict[str, tuple[int, int, int]] = {}

    def execute(self, graph: Graph) -> None:
        for node_id, new_color in self.color_map.items():
            node = graph.get_node(node_id)
            if node:
                self.old_colors[node_id] = node.color
                node.color = new_color

    def undo(self, graph: Graph) -> None:
        for node_id, old_color in self.old_colors.items():
            node = graph.get_node(node_id)
            if node:
                node.color = old_color


class CommandHistory:
    """Manages the undo and redo stacks."""

    def __init__(self) -> None:
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []

    def execute(self, command: Command, graph: Graph) -> None:
        """Run a command and push it to the undo stack, clearing the redo stack."""
        command.execute(graph)
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def push(self, command: Command) -> None:
        """Directly append a pre-executed command to the undo stack."""
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self, graph: Graph) -> None:
        """Undo the last command."""
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.undo(graph)
        self.redo_stack.append(command)

    def redo(self, graph: Graph) -> None:
        """Redo the last undone command."""
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        command.execute(graph)
        self.undo_stack.append(command)

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
