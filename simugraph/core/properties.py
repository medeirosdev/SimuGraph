from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simugraph.core.graph import Graph

class GraphProperties:
    def __init__(self, graph: Graph):
        self.graph = graph

    def is_connected(self) -> bool:
        nodes = list(self.graph.nodes())
        if not nodes:
            return True
        
        # Weak connectivity: treat all edges as undirected
        visited = set()
        adj = {n.id: [] for n in nodes}
        for e in self.graph.edges():
            adj[e.u].append(e.v)
            adj[e.v].append(e.u)
        
        queue = deque([nodes[0].id])
        visited.add(nodes[0].id)
        while queue:
            curr = queue.popleft()
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(nodes)

    def is_bipartite(self) -> tuple[bool, dict[str, int]]:
        nodes = list(self.graph.nodes())
        if not nodes:
            return True, {}

        # Treat as undirected for bipartiteness check
        adj = {n.id: [] for n in nodes}
        for e in self.graph.edges():
            adj[e.u].append(e.v)
            adj[e.v].append(e.u)

        color = {}
        for start_node in nodes:
            if start_node.id in color:
                continue
            
            queue = deque([start_node.id])
            color[start_node.id] = 0
            
            while queue:
                curr = queue.popleft()
                curr_color = color[curr]
                
                for neighbor in adj[curr]:
                    if neighbor not in color:
                        color[neighbor] = 1 - curr_color
                        queue.append(neighbor)
                    elif color[neighbor] == curr_color:
                        return False, {}
        return True, color

    def has_cycle(self) -> bool:
        nodes = list(self.graph.nodes())
        if not nodes:
            return False

        has_directed = any(e.directed for e in self.graph.edges())
        visited = set()

        if has_directed:
            rec_stack = set()
            def dfs_directed(u: str) -> bool:
                visited.add(u)
                rec_stack.add(u)
                for neighbor in self.graph.neighbors(u):
                    v = neighbor.id
                    if v not in visited:
                        if dfs_directed(v):
                            return True
                    elif v in rec_stack:
                        return True
                rec_stack.remove(u)
                return False

            for n in nodes:
                if n.id not in visited:
                    if dfs_directed(n.id):
                        return True
            return False
        else:
            # Undirected cycle detection: can't traverse back immediately to the parent
            parent = {}
            def dfs_undirected(u: str) -> bool:
                visited.add(u)
                for neighbor in self.graph.neighbors(u):
                    v = neighbor.id
                    if v not in visited:
                        parent[v] = u
                        if dfs_undirected(v):
                            return True
                    elif parent.get(u) != v:
                        return True
                return False

            for n in nodes:
                if n.id not in visited:
                    parent[n.id] = None
                    if dfs_undirected(n.id):
                        return True
            return False

    def is_tree(self) -> bool:
        nodes = list(self.graph.nodes())
        if not nodes:
            return False
        # Tree is connected and has no cycles
        return self.is_connected() and not self.has_cycle()

    def diameter(self) -> float:
        nodes = list(self.graph.nodes())
        n = len(nodes)
        if n <= 1:
            return 0.0

        # Compute all-pairs shortest paths using Floyd-Warshall
        id_to_idx = {node.id: i for i, node in enumerate(nodes)}
        dist = [[float('inf')] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0.0

        for edge in self.graph.edges():
            u_idx = id_to_idx.get(edge.u)
            v_idx = id_to_idx.get(edge.v)
            if u_idx is not None and v_idx is not None:
                if edge.weight < dist[u_idx][v_idx]:
                    dist[u_idx][v_idx] = float(edge.weight)
                if not edge.directed:
                    if edge.weight < dist[v_idx][u_idx]:
                        dist[v_idx][u_idx] = float(edge.weight)

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        max_dist = 0.0
        for i in range(n):
            for j in range(n):
                if dist[i][j] != float('inf') and dist[i][j] > max_dist:
                    max_dist = dist[i][j]

        if not self.is_connected():
            return float('inf')
        return max_dist

    def chromatic_number(self) -> int:
        nodes = list(self.graph.nodes())
        if not nodes:
            return 0
        # Welch-Powell graph coloring upper bound
        nodes_sorted = sorted(nodes, key=lambda n: (-self.graph.degree(n.id), n.label))
        colors = {}
        for node in nodes_sorted:
            neighbor_colors = {colors[nb.id] for nb in self.graph.neighbors(node.id) if nb.id in colors}
            color = 0
            while color in neighbor_colors:
                color += 1
            colors[node.id] = color
        return len(set(colors.values()))

    def degree_centrality(self) -> dict[str, float]:
        nodes = list(self.graph.nodes())
        n = len(nodes)
        if n <= 1:
            return {node.id: 0.0 for node in nodes}
        
        return {node.id: self.graph.degree(node.id) / (n - 1) for node in nodes}

    def closeness_centrality(self) -> dict[str, float]:
        nodes = list(self.graph.nodes())
        n = len(nodes)
        centrality = {}
        if n <= 1:
            return {node.id: 0.0 for node in nodes}

        # Floyd-Warshall/BFS distance computation
        id_to_idx = {node.id: i for i, node in enumerate(nodes)}
        dist = [[float('inf')] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0.0

        for edge in self.graph.edges():
            u_idx = id_to_idx.get(edge.u)
            v_idx = id_to_idx.get(edge.v)
            if u_idx is not None and v_idx is not None:
                if edge.weight < dist[u_idx][v_idx]:
                    dist[u_idx][v_idx] = float(edge.weight)
                if not edge.directed:
                    if edge.weight < dist[v_idx][u_idx]:
                        dist[v_idx][u_idx] = float(edge.weight)

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

        for u in nodes:
            u_idx = id_to_idx[u.id]
            sum_dist = 0.0
            reach_count = 0
            for v in nodes:
                v_idx = id_to_idx[v.id]
                d = dist[u_idx][v_idx]
                if d != float('inf') and u_idx != v_idx:
                    sum_dist += d
                    reach_count += 1
            
            if sum_dist == 0.0:
                centrality[u.id] = 0.0
            else:
                centrality[u.id] = (reach_count / (n - 1)) * (reach_count / sum_dist)
        return centrality

    def betweenness_centrality(self) -> dict[str, float]:
        nodes = list(self.graph.nodes())
        betweenness = {node.id: 0.0 for node in nodes}
        
        for s in nodes:
            S = []
            P = {node.id: [] for node in nodes}
            sigma = {node.id: 0.0 for node in nodes}
            sigma[s.id] = 1.0
            d = {node.id: -1 for node in nodes}
            d[s.id] = 0
            
            queue = deque([s.id])
            while queue:
                v = queue.popleft()
                S.append(v)
                for neighbor in self.graph.neighbors(v):
                    w = neighbor.id
                    if d[w] < 0:
                        d[w] = d[v] + 1
                        queue.append(w)
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)
            
            delta = {node.id: 0.0 for node in nodes}
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s.id:
                    betweenness[w] += delta[w]
        
        n = len(nodes)
        scale = 1.0
        if n > 2:
            has_directed = any(e.directed for e in self.graph.edges())
            factor = (n - 1) * (n - 2)
            if not has_directed:
                factor *= 2
            scale = 1.0 / factor if factor > 0 else 1.0

        for nid in betweenness:
            betweenness[nid] *= scale
            
        return betweenness
