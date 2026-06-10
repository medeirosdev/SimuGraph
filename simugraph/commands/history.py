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


class ChangeNodeWeightCommand(Command):
    def __init__(self, node_id: str, old_weight: float, new_weight: float) -> None:
        self.node_id = node_id
        self.old_weight = old_weight
        self.new_weight = new_weight

    def execute(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.weight = self.new_weight

    def undo(self, graph: Graph) -> None:
        node = graph.get_node(self.node_id)
        if node:
            node.weight = self.old_weight


class ChangeEdgeWeightCommand(Command):
    def __init__(self, edge_id: str, old_weight: float, new_weight: float) -> None:
        self.edge_id = edge_id
        self.old_weight = old_weight
        self.new_weight = new_weight

    def execute(self, graph: Graph) -> None:
        edge = graph.get_edge(self.edge_id)
        if edge:
            edge.weight = self.new_weight

    def undo(self, graph: Graph) -> None:
        edge = graph.get_edge(self.edge_id)
        if edge:
            edge.weight = self.old_weight


class MoveNodesCommand(Command):
    """Command to move a group of nodes simultaneously."""
    def __init__(self, moves: dict[str, tuple[tuple[float, float], tuple[float, float]]]) -> None:
        # moves maps node_id -> (old_pos, new_pos)
        self.moves = moves

    def execute(self, graph: Graph) -> None:
        for node_id, (_, new_pos) in self.moves.items():
            node = graph.get_node(node_id)
            if node:
                node.x, node.y = new_pos

    def undo(self, graph: Graph) -> None:
        for node_id, (old_pos, _) in self.moves.items():
            node = graph.get_node(node_id)
            if node:
                node.x, node.y = old_pos


class RemoveNodesCommand(Command):
    """Command to remove a group of nodes and their incident edges simultaneously."""
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def execute(self, graph: Graph) -> None:
        for node in self.nodes:
            graph.remove_node(node.id)

    def undo(self, graph: Graph) -> None:
        for node in self.nodes:
            graph.add_node(node)
        for edge in self.edges:
            graph.add_edge(edge)


class PasteSubgraphCommand(Command):
    """Command to paste a copied subgraph with offset and new IDs."""
    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def execute(self, graph: Graph) -> None:
        for node in self.nodes:
            graph.add_node(node)
        for edge in self.edges:
            graph.add_edge(edge)

    def undo(self, graph: Graph) -> None:
        for edge in self.edges:
            graph.remove_edge(edge.id)
        for node in self.nodes:
            graph.remove_node(node.id)


class CommandHistory:
    """Manages the undo and redo stacks."""

    def __init__(self) -> None:
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self.on_change_callbacks: list[callable] = []

    def execute(self, command: Command, graph: Graph) -> None:
        """Run a command and push it to the undo stack, clearing the redo stack."""
        command.execute(graph)
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self._trigger_on_change()

    def push(self, command: Command) -> None:
        """Directly append a pre-executed command to the undo stack."""
        self.undo_stack.append(command)
        self.redo_stack.clear()
        self._trigger_on_change()

    def undo(self, graph: Graph) -> None:
        """Undo the last command."""
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.undo(graph)
        self.redo_stack.append(command)
        self._trigger_on_change()

    def redo(self, graph: Graph) -> None:
        """Redo the last undone command."""
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        command.execute(graph)
        self.undo_stack.append(command)
        self._trigger_on_change()

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._trigger_on_change()

    def _trigger_on_change(self) -> None:
        for cb in self.on_change_callbacks:
            cb()
