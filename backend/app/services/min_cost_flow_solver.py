import math
from app.models.flow_models import FlowEdge
from app.services.spfa import spfa
from app.utils.graph_distances import compute_garage_distances
import networkx as nx


def add_edge(graph, u, v, capacity, cost):
    graph[u].append(FlowEdge(v, capacity, cost, len(graph[v])))
    graph[v].append(FlowEdge(u, 0, -cost, len(graph[u]) - 1))


def solve_min_cost_flow(G, R, routes_obj, garages_supply):
    """
    Returns: networkx.MultiGraph (solution graph)
    """

    routes = routes_obj["obj"]

    # --- index mapping ---
    garage_nodes = list(garages_supply.keys())
    route_nodes = [r.number for r in routes]

    SRC = 0
    garage_offset = 1
    route_offset = garage_offset + len(garage_nodes)
    SINK = route_offset + len(route_nodes)

    N = SINK + 1
    graph = [[] for _ in range(N)]

    # --- distances ---
    distances = compute_garage_distances(G, garage_nodes)

    # --- source -> garages ---
    for i, g in enumerate(garage_nodes):
        add_edge(graph, SRC, garage_offset + i, garages_supply[g], 0)

    # --- routes -> sink ---
    route_index = {r.number: idx for idx, r in enumerate(routes)}

    for r in routes:
        idx = route_index[r.number]
        add_edge(graph, route_offset + idx, SINK, r.demand, 0)

    # --- garages -> routes ---
    for gi, g in enumerate(garage_nodes):
        dist_map = distances[g]

        for r in routes:
            idx = route_index[r.number]

            # route endpoints
            seq = r.sequence
            u = seq[0]
            v = seq[-1]

            cost = min(dist_map.get(u, math.inf), dist_map.get(v, math.inf))

            if cost < math.inf:
                add_edge(graph, garage_offset + gi, route_offset + idx, math.inf, cost)

    # --- min cost flow ---
    flow = 0
    cost = 0
    total_demand = routes_obj["total_demand"]

    while flow < total_demand:
        dist, parent = spfa(graph, SRC)
        if dist[SINK] == math.inf:
            raise Exception("Infeasible: not enough garage supply")

        # find bottleneck
        f = math.inf
        v = SINK
        while v != SRC:
            u, ei = parent[v]
            f = min(f, graph[u][ei].capacity)
            v = u

        # apply flow
        v = SINK
        while v != SRC:
            u, ei = parent[v]
            e = graph[u][ei]
            e.capacity -= f
            graph[v][e.rev].capacity += f
            cost += f * e.cost
            v = u

        flow += f

    # --- build solution graph ---
    sol = nx.MultiGraph()
    
    # add nodes
    for g in garage_nodes:
        sol.add_node(g, is_garage=True, label=g)

    for r in route_nodes:
        sol.add_node(r, is_route=True, label=f"Route {r}")


    for gi, g in enumerate(garage_nodes):
        u = garage_offset + gi
        for e in graph[u]:
            if route_offset <= e.to < route_offset + len(route_nodes):
                used = graph[e.to][e.rev].capacity
                if used > 0:
                    r_idx = e.to - route_offset
                    route_number = route_nodes[r_idx]

                    sol.add_edge(
                        g,
                        route_number,
                        flow=used,
                        cost=e.cost,
                        route=route_number
                    )


    return sol
