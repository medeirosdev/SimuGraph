from __future__ import annotations
import os
import pytest
from simugraph.core.graph import Graph
from simugraph.core.node import Node
from simugraph.core.edge import Edge
from simugraph.io.matrix import AdjacencyMatrixIO
from simugraph.io.graphml import GraphMLIO
from simugraph.io.gexf import GexfIO
from simugraph.io.dot_format import DotFormatIO

def test_adjacency_matrix_io(tmp_path):
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    
    e1 = Edge(u="n1", v="n2", weight=4.5, directed=False)
    g.add_edge(e1)
    
    filepath = os.path.join(tmp_path, "matrix.csv")
    AdjacencyMatrixIO.export_matrix(g, filepath)
    
    # Import back into a fresh graph
    g2 = Graph()
    AdjacencyMatrixIO.import_matrix(g2, filepath)
    
    assert g2.node_count() == 2
    assert g2.edge_count() == 1
    imported_edge = list(g2.edges())[0]
    assert imported_edge.weight == 4.5
    assert not imported_edge.directed

def test_graphml_io(tmp_path):
    g = Graph()
    n1 = Node(id="n1", label="Node1", x=100.0, y=200.0)
    n2 = Node(id="n2", label="Node2", x=300.0, y=400.0)
    g.add_node(n1)
    g.add_node(n2)
    
    e1 = Edge(u="n1", v="n2", weight=12.0, directed=True)
    g.add_edge(e1)
    
    filepath = os.path.join(tmp_path, "test.graphml")
    GraphMLIO.export_graphml(g, filepath)
    
    # Import back
    g2 = Graph()
    GraphMLIO.import_graphml(g2, filepath)
    
    assert g2.node_count() == 2
    assert g2.edge_count() == 1
    imported_edge = list(g2.edges())[0]
    assert imported_edge.weight == 12.0
    assert imported_edge.directed

def test_gexf_export(tmp_path):
    g = Graph()
    n1 = Node(id="n1", label="A", x=100.0, y=200.0)
    n2 = Node(id="n2", label="B", x=300.0, y=400.0)
    g.add_node(n1)
    g.add_node(n2)
    
    e1 = Edge(u="n1", v="n2", weight=5.0)
    g.add_edge(e1)
    
    filepath = os.path.join(tmp_path, "test.gexf")
    GexfIO.export_gexf(g, filepath)
    
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "gexf" in content
        assert "Node1" not in content # label is "A", "B"
        assert "A" in content

def test_dot_export(tmp_path):
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    
    e1 = Edge(u="n1", v="n2", weight=2.5, directed=True)
    g.add_edge(e1)
    
    filepath = os.path.join(tmp_path, "test.dot")
    DotFormatIO.export_dot(g, filepath)
    
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "digraph" in content
        assert "A" in content
        assert "B" in content

def test_import_top_csv():
    g = Graph()
    AdjacencyMatrixIO.import_matrix(g, "/home/medeiros/Projetos/SimuGraph/top.csv")
    assert g.node_count() == 20
    assert g.edge_count() > 0


def test_clipboard_io():
    from simugraph.io.clipboard_io import ClipboardIO
    
    g = Graph()
    n1 = Node(id="n1", label="A")
    n2 = Node(id="n2", label="B")
    g.add_node(n1)
    g.add_node(n2)
    e1 = Edge(u="n1", v="n2", weight=3.5, directed=True)
    g.add_edge(e1)
    
    exported = ClipboardIO.export_tuples(g)
    # Check that exported text is correct
    assert "A" in exported
    assert "B" in exported
    assert "3.5" in exported
    
    # Import back
    g2 = Graph()
    ClipboardIO.import_tuples(g2, exported)
    
    assert g2.node_count() == 2
    assert g2.edge_count() == 1
    
    nodes = list(g2.nodes())
    labels = {n.label for n in nodes}
    assert "A" in labels
    assert "B" in labels
    
    edge = list(g2.edges())[0]
    assert edge.weight == 3.5
    assert edge.directed


