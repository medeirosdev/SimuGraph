from __future__ import annotations
import pytest
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.core.edge import Edge

def test_add_remove_node():
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    assert g.node_count() == 2
    assert g.get_node("n1").label == "A"
    
    g.remove_node("n1")
    assert g.node_count() == 1
    assert g.get_node("n1") is None

def test_add_remove_edge():
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    
    e1 = Edge(u="n1", v="n2", weight=3.5, directed=True)
    g.add_edge(e1)
    assert g.edge_count() == 1
    assert g.degree("n1") == 1
    
    g.remove_edge(e1.id)
    assert g.edge_count() == 0

def test_graph_properties():
    from simugraph.core.properties import GraphProperties
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    
    props = GraphProperties(g)
    assert not props.is_connected() # no edges yet
    
    e1 = Edge(u="n1", v="n2")
    g.add_edge(e1)
    assert props.is_connected()
