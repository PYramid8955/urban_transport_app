import networkx as nx
import math
import heapq


# MINIMUM COST FLOW (SSP) – Modul Final

class SSP_MinCostFlow:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v, capacity, cost):
        if u not in self.graph: self.graph[u] = []
        if v not in self.graph: self.graph[v] = []
        self.graph[u].append([v, capacity, cost, len(self.graph[v])])
        self.graph[v].append([u, 0, -cost, len(self.graph[u]) - 1])

    def load_from_networkx(self, G: nx.DiGraph):
        for u, v, data in G.edges(data=True):
            cap = data.get("capacity", 0)
            cost = data.get("time", 1)
            self.add_edge(u, v, cap, cost)

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

    def get_edge_flows(self):
        used = []
        for u in self.graph:
            for (v, cap, cost, rev) in self.graph[u]:
                used_flow = self.graph[v][rev][1]
                if used_flow > 0 and cost >= 0:
                    used.append((u, v, used_flow, cost))
        return used

def compute_bus_schedule(G, source, sink, demand_people, bus_capacity, total_buses):
    mcf = SSP_MinCostFlow()
    mcf.load_from_networkx(G)

    required_buses = math.ceil(demand_people / bus_capacity)
    max_buses_used = min(required_buses, total_buses)

    flow, total_cost = mcf.min_cost_flow(source, sink, max_buses_used)
    routes = mcf.get_edge_flows()

    final_routes = []
    for u, v, autobuze, cost in routes:
        interval = 60 / autobuze if autobuze > 0 else None
        final_routes.append({
            "from": u,
            "to": v,
            "buses": autobuze,
            "interval_minutes": interval
        })

    return {
        "routes": final_routes,
        "total_cost": total_cost,
    }

