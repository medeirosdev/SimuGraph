# SimuGraph

![SimuGraph Banner](assets/banner.png)

SimuGraph is an interactive desktop graph simulator and visualizer built with Pygame. It allows users to build, manipulate, and analyze graphs dynamically while watching step-by-step algorithms execute with real-time feedback.

---

## Features

### Interactive Editor and Canvas
* Creation of nodes and directed/undirected edges using direct mouse inputs.
* Real-time dragging of single or grouped vertices with alignment snapping.
* Custom weight values for nodes and edges.
* Right-click Context Menus for quick properties modification (Rename, Pin/Unpin, Change Color, Set as Source, Edit Weights, Delete).
* Anti-aliased high-performance rendering supporting camera panning and zooming.
* Interactive Minimap overlay at the bottom-right corner showing graph bounds and visible viewport rectangle.

### Advanced File I/O and Exporting
* Full serialization of graph state to JSON-based .sgraph files.
* GraphML import and export.
* GEXF export for Gephi.
* DOT format export for Graphviz rendering.
* Adjacency Matrix import and export via CSV.
* PNG screenshot capturing.
* Algorithm step-by-step recording and GIF export.

### Graph Generators
* Random Graph (Erdos-Renyi model)
* Complete Graph
* Bipartite Graph
* Tree Graph
* Grid Graph
* Cycle Graph
* Scale-free Graph (Barabasi-Albert model)

### Algorithm Runner and Visualization
* Visual representations of node states (Visited, Frontier, Highlighted Edges, Source).
* Multi-control Execution Panel (Play/Pause, Step Forward/Backward, Hz Speed Slider).
* Interactive Node Badges rendering distances, costs, and internal state parameters.
* Detail Inspector displaying data structures, queues, and priority updates.
* Export Results option to compile final logs to a plain text file.
* Supported Algorithms:
  * Breadth-First Search (BFS)
  * Depth-First Search (DFS)
  * Dijkstra's Shortest Path
  * Bellman-Ford (Shortest Path with negative weights)
  * Floyd-Warshall All-Pairs Shortest Path
  * A* Shortest Path (Euclidean heuristic)
  * Kruskal's Minimum Spanning Tree
  * Prim's Minimum Spanning Tree
  * Topological Sort (with cycle checking)
  * Strongly Connected Components (Tarjan's algorithm)
  * Bridges and Articulation Points identification
  * Greedy Graph Coloring
  * Eulerian Path and Circuit detection

### Plugin System
* Extensible algorithm loader that discovers custom algorithms in the plugins directory.
* Custom algorithms automatically register inside the Algorithms menu.

### Accessibility and Keyboard Navigation
* Tab / Shift+Tab to cycle through nodes, centering camera focus automatically.
* Enter key to rename the selected node.
* Arrow keys to move selected nodes in world space.
* Ctrl+F search bar to find and select nodes by label.

---

## Planned Features

* Flow Networks: Edmonds-Karp and Ford-Fulkerson implementations with visual capacity changes and bottleneck tracking.
* Performance Analysis Panel: Compare execution times of multiple shortest-path algorithms on the same graph topology.
* Customizable Shapes: Support for square, hexagonal, or custom node outlines.

---

## Installation and Execution

### Requirements
* Python 3.10 or higher
* Pygame
* Pillow (for GIF export support)

### Setup
1. Create a virtual environment and activate it:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulator:
```bash
python main.py
```

4. Run the simulator with CLI parameters to auto-load files and execute algorithms:
```bash
python main.py --file path/to/graph.sgraph --algo dijkstra --source A
```

---

## Controls Cheatsheet

### Global Keyboard Controls
* Space: Play/Pause Algorithm Execution
* Right Arrow: Next Step (Algorithm Mode)
* Left Arrow: Previous Step (Algorithm Mode)
* Shift + Right Arrow: Jump to last step
* Shift + Left Arrow: Jump to first step
* Escape: Stop Algorithm / Cancel Action / Exit
* Ctrl + Z: Undo last modification
* Ctrl + Y: Redo last modification
* Ctrl + T: Cycle through themes
* Ctrl + F: Search node by label
* Ctrl + S: Save graph
* Ctrl + Shift + S: Save graph as...
* Ctrl + O: Open graph
* Ctrl + E: Export PNG screenshot
* Ctrl + C: Copy selected subgraph
* Ctrl + V: Paste subgraph
* Tab: Cycle selected node forward
* Shift + Tab: Cycle selected node backward
* Enter: Rename selected node
* Arrow keys: Move selected nodes (10px)
* L: Run Spring Force Layout
* S: Toggle Grid Snapping
* D: Toggle Directed Edges
* F: Fit graph to screen
* 0: Reset camera zoom
* ?: Toggle Cheatsheet overlay

### Tool Selection
* V: Select Tool
* N: Node Tool
* E: Edge Tool
* R: Remove Tool
