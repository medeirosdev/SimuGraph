from __future__ import annotations
import pytest
from simugraph.generators import (
    generate_complete,
    generate_bipartite,
    generate_tree,
    generate_grid,
    generate_cycle,
    generate_random_graph,
    generate_barabasi_albert
)

def test_generate_complete():
    nodes, edges = generate_complete(5)
    assert len(nodes) == 5
    # Complete graph has n*(n-1)/2 edges
    assert len(edges) == 10

def test_generate_bipartite():
    nodes, edges = generate_bipartite(3, 4)
    assert len(nodes) == 7
    # Complete bipartite graph has n1 * n2 edges
    assert len(edges) == 12

def test_generate_tree():
    nodes, edges = generate_tree(6)
    assert len(nodes) == 6
    # A tree on n nodes always has n - 1 edges
    assert len(edges) == 5

def test_generate_grid():
    nodes, edges = generate_grid(3, 3)
    assert len(nodes) == 9
    # 3x3 grid has 2*3*(3-1) = 12 edges
    assert len(edges) == 12

def test_generate_cycle():
    nodes, edges = generate_cycle(6)
    assert len(nodes) == 6
    assert len(edges) == 6

def test_generate_random():
    # Erdős–Rényi graph
    nodes, edges = generate_random_graph(10, 0.5)
    assert len(nodes) == 10

def test_generate_barabasi_albert():
    nodes, edges = generate_barabasi_albert(15, 2)
    assert len(nodes) == 15
