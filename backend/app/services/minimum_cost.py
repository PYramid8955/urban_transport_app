import math
import heapq
import networkx as nx



#  ALGORITM MCF – SSP (CORECT)

class SSP_MinCostFlow:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v, capacity, cost):
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        # muchie directă
        self.graph[u].append([v, capacity, cost, len(self.graph[v])])
        # muchie inversă
        self.graph[v].append([u, 0, -cost, len(self.graph[u]) - 1])

    def min_cost_flow(self, source, sink, max_flow):
        total_cost = 0
        flow = 0
        potential = {node: 0 for node in self.graph}

        while flow < max_flow:
            dist = {node: math.inf for node in self.graph}
            parent = {node: (None, None) for node in self.graph}
            dist[source] = 0

            pq = [(0, source)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue

                for i, (v, cap, cost, rev) in enumerate(self.graph[u]):
                    if cap > 0:
                        new_cost = d + cost + potential[u] - potential[v]
                        if new_cost < dist[v]:
                            dist[v] = new_cost
                            parent[v] = (u, i)
                            heapq.heappush(pq, (new_cost, v))

            if dist[sink] == math.inf:
                break

            for node in self.graph:
                if dist[node] < math.inf:
                    potential[node] += dist[node]

            add_flow = max_flow - flow
            v = sink
            while v != source:
                u, i = parent[v]
                add_flow = min(add_flow, self.graph[u][i][1])
                v = u

            v = sink
            while v != source:
                u, i = parent[v]
                self.graph[u][i][1] -= add_flow
                rev = self.graph[u][i][3]
                self.graph[v][rev][1] += add_flow
                total_cost += self.graph[u][i][2] * add_flow
                v = u

            flow += add_flow

        return flow, total_cost
