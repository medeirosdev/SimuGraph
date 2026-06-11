from __future__ import annotations
import pytest
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.core.properties import GraphProperties

def test_properties_connected_and_tree():
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    n3 = Node(id="n3", label="C")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    props = GraphProperties(g)
    assert not props.is_connected()
    assert not props.is_tree()
    
    # Path: A - B - C
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", directed=False))
    
    assert props.is_connected()
    assert props.is_tree()
    assert not props.has_cycle()
    
    # Add cycle: C - A
    g.add_edge(Edge(id="e3", u="n3", v="n1", directed=False))
    assert props.has_cycle()
    assert not props.is_tree()

def test_properties_bipartite():
    g = Graph()
    n1 = Node(id="n1")
    n2 = Node(id="n2")
    n3 = Node(id="n3")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    props = GraphProperties(g)
    # Even a cycle C3 (triangle) is not bipartite
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", directed=False))
    
    is_bip, colors = props.is_bipartite()
    assert is_bip # Path of length 2 is bipartite
    
    g.add_edge(Edge(id="e3", u="n3", v="n1", directed=False))
    is_bip, colors = props.is_bipartite()
    assert not is_bip

def test_properties_diameter():
    g = Graph()
    n1 = Node(id="n1")
    n2 = Node(id="n2")
    n3 = Node(id="n3")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    # A - B - C, weights 1.5, 2.0
    g.add_edge(Edge(id="e1", u="n1", v="n2", weight=1.5, directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", weight=2.0, directed=False))
    
    props = GraphProperties(g)
    # Connected diameter is 3.5
    assert props.diameter() == 3.5

def test_properties_chromatic_number():
    g = Graph()
    n1 = Node(id="n1")
    n2 = Node(id="n2")
    n3 = Node(id="n3")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    props = GraphProperties(g)
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", directed=False))
    g.add_edge(Edge(id="e3", u="n3", v="n1", directed=False))
    
    # Triangle needs 3 colors
    assert props.chromatic_number() == 3

def test_properties_centrality():
    g = Graph()
    n1 = Node(id="n1")
    n2 = Node(id="n2")
    n3 = Node(id="n3")
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    
    g.add_edge(Edge(id="e1", u="n1", v="n2", directed=False))
    g.add_edge(Edge(id="e2", u="n2", v="n3", directed=False))
    
    props = GraphProperties(g)
    
    deg = props.degree_centrality()
    # Node B (n2) has degree 2/2 = 1.0, others have 0.5
    assert deg["n2"] == 1.0
    assert deg["n1"] == 0.5
    
    clos = props.closeness_centrality()
    # B is 1 step from A and C. A is 1 step from B and 2 steps from C.
    # closeness(B) = 1.0
    assert clos["n2"] == 1.0
    assert clos["n1"] < 1.0
    
    bet = props.betweenness_centrality()
    # B is on the only path A-C. With scaling for undirected n=3, bet[B] = 2 * (1 / 4) = 0.5
    assert bet["n2"] == 0.5
    assert bet["n1"] == 0.0
