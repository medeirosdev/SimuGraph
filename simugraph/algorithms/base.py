"""
Abstract base class and state representations for animated step-by-step algorithms.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

@dataclass
class AlgoState:
    visited: set[str] = field(default_factory=set)
    frontier: set[str] = field(default_factory=set)
    path: list[str] = field(default_factory=list)
    distances: dict[str, float] = field(default_factory=dict)
    highlighted_edges: set[str] = field(default_factory=set)
    scc_groups: list[set[str]] = field(default_factory=list)
    colors: dict[str, int] = field(default_factory=dict)
    message: str = ""
    step_index: int = 0
    total_steps: int = 0
    detail_text: str = ""

class StepAlgorithm(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def requires_source(self) -> bool:
        return True

    @abstractmethod
    def steps(self, graph: Graph, source: str | None = None) -> list[AlgoState]:
        """
        Pre-computes and returns a list of AlgoState objects representing
        each step of the algorithm.
        """
        pass


import pygame

class AlgoRunner:
    def __init__(self) -> None:
        self.algorithm: StepAlgorithm | None = None
        self.states: list[AlgoState] = []
        self.current_step_idx: int = 0
        self.playing: bool = False
        self.speed_fps: float = 1.0  # steps per second
        self.last_step_ticks: int = 0
        self.source_node_id: str | None = None

    def start(self, algorithm: StepAlgorithm, graph: Graph, source_node_id: str | None = None) -> None:
        self.algorithm = algorithm
        self.source_node_id = source_node_id
        self.states = algorithm.steps(graph, source_node_id)
        self.current_step_idx = 0
        self.playing = False
        self.last_step_ticks = pygame.time.get_ticks()

    def stop(self) -> None:
        self.algorithm = None
        self.states = []
        self.current_step_idx = 0
        self.playing = False

    @property
    def current_state(self) -> AlgoState | None:
        if not self.states:
            return None
        return self.states[self.current_step_idx]

    def step_forward(self) -> None:
        if self.states:
            self.current_step_idx = min(len(self.states) - 1, self.current_step_idx + 1)

    def step_backward(self) -> None:
        if self.states:
            self.current_step_idx = max(0, self.current_step_idx - 1)

    def update(self) -> None:
        if not self.playing or not self.states:
            return
        
        now = pygame.time.get_ticks()
        ms_per_step = 1000.0 / max(0.1, self.speed_fps)
        if now - self.last_step_ticks >= ms_per_step:
            if self.current_step_idx < len(self.states) - 1:
                self.current_step_idx += 1
                self.last_step_ticks = now
            else:
                self.playing = False

    def export_results(self, filename: str) -> None:
        """
        Exports the details of the final algorithm state to a text file.
        """
        if not self.states:
            return
        
        final_state = self.states[-1]
        with open(filename, "w") as f:
            f.write(f"Algorithm: {self.algorithm.name if self.algorithm else 'Unknown'}\n")
            if self.source_node_id:
                f.write(f"Source Node ID: {self.source_node_id}\n")
            f.write(f"Steps Executed: {len(self.states)}\n\n")
            f.write("--- Final State Details ---\n")
            f.write(f"Message: {final_state.message}\n")
            f.write(f"{final_state.detail_text}\n")
