from __future__ import annotations
import pytest
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.algorithms import BFS, DFS, Dijkstra, TarjanSCC, Kruskal, AStar, EulerianPathCircuit

def create_simple_graph() -> Graph:
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    n3 = Node(id="n3", label="C")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    # Path: A - B - C
    g.add_edge(Edge(id="e1", u="n1", v="n2", weight=1.0, directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", weight=2.0, directed=False))
    return g

def test_bfs():
    g = create_simple_graph()
    algo = BFS()
    states = algo.steps(g, source="n1")
    assert len(states) > 0
    final_state = states[-1]
    assert "n1" in final_state.visited
    assert "n2" in final_state.visited
    assert "n3" in final_state.visited

def test_dfs():
    g = create_simple_graph()
    algo = DFS()
    states = algo.steps(g, source="n1")
    assert len(states) > 0
    final_state = states[-1]
    assert "n1" in final_state.visited
    assert "n2" in final_state.visited
    assert "n3" in final_state.visited

def test_dijkstra():
    g = create_simple_graph()
    algo = Dijkstra()
    states = algo.steps(g, source="n1")
    assert len(states) > 0
    final_state = states[-1]
    # Distances from A (n1): A=0, B=1.0, C=3.0
    assert final_state.distances["n1"] == 0.0
    assert final_state.distances["n2"] == 1.0
    assert final_state.distances["n3"] == 3.0

def test_tarjan_scc():
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    
    # 2-cycle makes them a single SCC
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=True))
    g.add_edge(Edge(id="e2", u="n2", v="n1", directed=True))
    
    algo = TarjanSCC()
    states = algo.steps(g)
    assert len(states) > 0
    final_state = states[-1]
    # Should find 1 SCC containing both nodes
    assert len(final_state.scc_groups) == 1
    assert "n1" in final_state.scc_groups[0]
    assert "n2" in final_state.scc_groups[0]

def test_kruskal():
    g = create_simple_graph()
    algo = Kruskal()
    states = algo.steps(g)
    assert len(states) > 0
    final_state = states[-1]
    # MST should include both edges
    assert len(final_state.highlighted_edges) == 2
    assert "e1" in final_state.highlighted_edges
    assert "e2" in final_state.highlighted_edges

def test_astar():
    g = Graph()
    n1 = Node(id="n1", label="A", x=0.0, y=0.0)
    n2 = Node(id="n2", label="B", x=100.0, y=0.0)
    n3 = Node(id="n3", label="C", x=100.0, y=100.0)
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    g.add_edge(Edge(id="e1", u="n1", v="n2", weight=10.0, directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", weight=5.0, directed=False))
    
    algo = AStar()
    # Path from A to C
    states = algo.steps(g, source="n1")
    assert len(states) > 0
    final_state = states[-1]
    assert final_state.path == ["n1", "n2", "n3"]
    assert "e1" in final_state.highlighted_edges
    assert "e2" in final_state.highlighted_edges

def test_eulerian():
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    n3 = Node(id="n3", label="C")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    # Triangle (Eulerian Circuit)
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", directed=False))
    g.add_edge(Edge(id="e3", u="n3", v="n1", directed=False))
    
    algo = EulerianPathCircuit()
    states = algo.steps(g)
    assert len(states) > 0
    final_state = states[-1]
    assert len(final_state.highlighted_edges) == 3

