# SimuGraph

![SimuGraph Banner](assets/banner.png)

SimuGraph is an interactive desktop graph simulator and visualizer built with Pygame. It allows users to build, manipulate, and analyze graphs dynamically while watching step-by-step algorithms execute with real-time feedback.

## Existing Features

### Interactive Editor and Canvas
* Creation of nodes and directed/undirected edges using direct mouse inputs.
* Real-time dragging of single or grouped vertices with alignment snapping.
* Custom weight values for nodes and edges.
* Right-click Context Menus for quick properties modification (Rename, Pin/Unpin, Change Color, Set as Source, Edit Weights, Delete).
* Anti-aliased high-performance rendering supporting camera panning and zooming.

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
  * Kruskal's Minimum Spanning Tree
  * Prim's Minimum Spanning Tree
  * Topological Sort (with cycle checking)
  * Strongly Connected Components (Tarjan's algorithm)
  * Bridges and Articulation Points identification

### System Architecture
* Complete Undo/Redo command history framework.
* Theme Engine with color palette presets (Dark, Light, Cyberpunk, etc.).
* Dynamic grid rendering adapting to camera scales.

---

## Planned Features

* JSON Graph Import/Export: Serialization of graph structures and coordinates.
* Flow Networks: Edmonds-Karp and Ford-Fulkerson implementations with visual capacity changes and bottleneck tracking.
* Performance Analysis Panel: Compare the execution times and operations of multiple shortest-path algorithms on the same graph topology.
* Vertex Label Auto-Generation: Intelligent labeling rules based on degrees or custom properties.
* Customizable Shapes: Support for square, hexagonal, or custom node outlines.

---

## Installation and Execution

### Requirements
* Python 3.8 or higher
* Pygame

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

---

## Controls Cheatsheet

### Global Keyboard Controls
* Space: Play/Pause Algorithm Execution
* Right Arrow: Next Step (Algorithm Mode)
* Left Arrow: Previous Step (Algorithm Mode)
* Up Arrow: Increase Algorithm Playback Speed
* Down Arrow: Decrease Algorithm Playback Speed
* Escape: Stop Algorithm / Cancel Action / Exit
* Ctrl + Z: Undo last modification
* Ctrl + Y: Redo last modification
* Ctrl + T: Cycle through themes
* L: Run Spring Force Layout
* S: Toggle Grid Snapping
* D: Toggle Directed Edges
* 0: Reset camera zoom
* ?: Toggle Cheatsheet overlay

### Tool Selection
* V: Select Tool
* N: Node Tool
* E: Edge Tool
* R: Remove Tool
