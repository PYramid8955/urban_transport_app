import heapq
import networkx as nx
import math

class AStarTransport:
    def __init__(self, graph, node_coords=None, heuristic_func=None):
        
        if isinstance(graph, (nx.Graph, nx.DiGraph)):
            self.graph = {
                n: {nbr: graph[n][nbr]['weight'] for nbr in graph.neighbors(n)}
                for n in graph.nodes
            }
        else:
            self.graph = graph

        self.node_coords = node_coords

        if heuristic_func:
            self.heuristic_func = heuristic_func
        elif node_coords:
            # Heuristica Euclidiană
            self.heuristic_func = lambda n, end: math.hypot(
                node_coords[end][0] - node_coords[n][0],
                node_coords[end][1] - node_coords[n][1]
            )
        else:
            self.heuristic_func = lambda n, end: 0

    def find_path(self, start_node, end_node):
       
        open_set = []
        heapq.heappush(open_set, (0, start_node, [start_node]))  
        g_scores = {start_node: 0}

        while open_set:
            f_score, current, path = heapq.heappop(open_set)

            if current == end_node:
                return {'path': path, 'total_time': g_scores[current]}

            for neighbor, cost in self.graph.get(current, {}).items():
                tentative_g = g_scores[current] + cost
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    f_score_neighbor = tentative_g + self.heuristic_func(neighbor, end_node)
                    heapq.heappush(open_set, (f_score_neighbor, neighbor, path + [neighbor]))

        return {'path': [], 'total_time': float('inf')}


