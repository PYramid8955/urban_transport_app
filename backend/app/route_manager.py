# here we combine everything
from app.services import *
import networkx as nx
from math import ceil
from app.models import Route
from app.utils import RouteDemandCalculator
from app.utils import sample, rand_num

class RouteManager:
    # the desired route lenght in minutes (approx.), one way
    # using a list to be able to return to the initial graph after removing edges
    def __init__(self, G: nx.Graph, route_length = 45, min_inter_station_time = 1, max_inter_station_time = 10, verbose: bool = False):
        self.Routes = []
        self.Routes_obj = {'obj': [], 'total_demand': 0}
        self.Garages = {}
        
        self.main_graph = G
        self.route_length = route_length
        self.min_inter_station_time = min_inter_station_time
        self.max_inter_station_time = max_inter_station_time
        
        self.RDC = RouteDemandCalculator(G)
        self.gen_routes(verbose)
        self.assign_random_garages(ratio=0.04)
        print(f'[GARAGES] Chosen garages: {self.Garages}')
        self.flow_solution = solve_min_cost_flow(
            G=self.main_graph,
            routes_obj=self.Routes_obj,
            garages_supply=self.Garages
        )

    def compute_time(self, path):
        res = 0
        for i in range(len(path)-1):
            res += self.main_graph[path[i]][path[i+1]]['travel_time']
        return res

    def compute_hub_graph(self, hubs, astar):
        hub_nodes = list([hub[1] for hub in hubs])
        G = nx.Graph()
        avg_time = 0

        # add nodes
        G.add_nodes_from(hub_nodes)

        for i in range(len(hub_nodes)):
            for j in range(i+1, len(hub_nodes)):
                u = hub_nodes[i]
                v = hub_nodes[j]

                res = astar.find_path(u, v)
                avg_time += self.compute_time(res['path'])

                G.add_edge(u, v, weight=res['total_time'])

        avg_time /= (len(hub_nodes) * (len(hub_nodes) - 1)) / 2
        return G, avg_time


    def assign_routes(self, R: nx.MultiGraph, route: list, number: int, astar: AStarTransport):
        demand = self.RDC.bottleneck_demand(route)
        self.Routes_obj['obj'].append(Route(route, number, demand))
        self.Routes_obj['total_demand'] += demand
        
        for i in range(len(route)-1):
            path = [route[i], route[i+1]] if self.main_graph.has_edge(route[i], route[i+1]) else astar.find_path(route[i], route[i+1])['path']
            for j in range(len(path)-1):
                R.add_edge(path[j], path[j+1], number = number, travel_time = self.main_graph[path[j]][path[j+1]]['travel_time'], 
                        traffic = self.main_graph[path[j]][path[j+1]]['traffic'], weight = self.main_graph[path[j]][path[j+1]]['weight'])
        return [number, route]


    def gen_routes(self, verbose:bool = False):
        G = self.main_graph

        R = nx.MultiGraph() # routes-only graph
        R.add_nodes_from(G.nodes())
        self.Routes = [R]

        astarG = AStarTransport(G)

        res = {'betweeness_centrality': betweenness_centrality(G, astarG, verbose=verbose), 'routes': []}
        print('Generated scores for all nodes with BC.')

        working_G = G

        avg_time = (self.min_inter_station_time+self.max_inter_station_time)/2
        while True:
            total_stations = working_G.number_of_nodes()
            stations_per_route = self.route_length/avg_time + 1
            if (int(stations_per_route) == 1): stations_per_route+=1
            k_clusters = ceil(total_stations/stations_per_route)
            #1. clustering
            parts, clusters = metis_partition(working_G, k=k_clusters, balance_tol=0.05, scale=100)
            #2. get routes
            for i, cluster in clusters.items():
                route, cost, _ = simulated_annealing(working_G, cluster, temperature=500, max_iter=500, alpha=0.97)
                res['routes'].append(self.assign_routes(R, route, len(res['routes']), astarG))
                if verbose: print(f"Used SA to generate route {res['routes'][-1][0]} with cost {cost}.")
                if cost == float('inf'): raise Exception("Can't have infinite cost!")
                if verbose:
                    print(f"\n=== ROUTE {res['routes'][-1][0]} ===")
                    print('\n'.join([f'{route[i]} -> {route[i+1]}' for i in range(0, len(route)-1, 1)]))
                

            if (len(clusters) == 1): return (R, res)
            #3. gen hubs    
            hubs = {pid: (float('-inf'), None) for pid in clusters}
            for pid, cluster in clusters.items():
                for node in cluster:
                    score = res['betweeness_centrality'][node]
                    if score > hubs[pid][0]:
                        hubs[pid] = (score, node)
            hubs_list = [hubs[pid] for pid in sorted(hubs.keys())]

            print('Computed hubs successfully!')
            #4. gen hub graph
            working_G, avg_time = self.compute_hub_graph(hubs_list, astarG)

            print('Computed hub graph successfully! Now running the whole thing again, but on the hubs')

    def remove_road(self, u, v):
        if not self.Routes[-1].has_edge(u, v):
            return False

        self.Routes.append(self.Routes[-1].copy())
        R = self.Routes[-1]

        # save attributes of the removed edge(s)
        old_edges_attrs = []
        route_numbers = set()

        for key, attrs in R[u][v].items():
            old_edges_attrs.append(attrs.copy())
            route_numbers.add(attrs["number"])

        # --- build temp graph ---
        temp_G = self.main_graph.copy()
        temp_G.remove_edge(u, v)

        # --- remove nodes belonging to the same route ---
        nodes_to_remove = set()

        for x, y, attrs in R.edges(data=True):
            if attrs.get("number") in route_numbers:
                nodes_to_remove.add(x)
                nodes_to_remove.add(y)

        # keep endpoints
        nodes_to_remove.discard(u)
        nodes_to_remove.discard(v)

        temp_G.remove_nodes_from(nodes_to_remove)

        # --- compute alternative path ---
        astar = AStarTransport(temp_G)
        result = astar.find_path(u, v)
        path = result["path"]
        print(path)

        if not path:
            return False

        # --- remove original edge(s) ---
        for k in list(R[u][v].keys()):
            R.remove_edge(u, v, key=k)

        # --- add detour edges using old attributes ---
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            for attrs in old_edges_attrs:
                R.add_edge(a, b, **attrs)

        return True


    def shortest_route_path(self, start, end):
        R = self.Routes[-1]
        G_simple = nx.Graph()

        for u, v, data in R.edges(data=True):
            w = data["weight"]

            if G_simple.has_edge(u, v):
                if w < G_simple[u][v]["weight"]:
                    G_simple[u][v]["weight"] = w
            else:
                G_simple.add_edge(u, v, weight=w)

        astar = AStarTransport(G_simple)
        result = astar.find_path(start, end)

        path = result["path"]
        path_processed = {'order': []}
        route_order = path_processed['order']

        for i in range(len(path)-1):
            u, v = path[i], path[i+1]

            if R.has_edge(u, v):
                # Check all parallel edges
                for key, attrs in R[u][v].items():
                    route_number = attrs["number"]

                    if not len(route_order) or route_order[-1] != route_number: route_order.append(route_number)

                    if route_number not in path_processed:
                        path_processed[route_number] = [u, v]
                    else:
                        path_processed[route_number].append(v)


        out = nx.MultiGraph()

        out.add_nodes_from(path)

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            if R.has_edge(u, v):
                for key, attrs in R[u][v].items():
                    out.add_edge(u, v, **attrs)

        return {'graph': out, 'path': path_processed}

    def assign_random_garages(
        self,
        ratio: float = 0.04,          # e.g. 4 garages per 100 nodes
        max_diff: int = 100,          # max difference between garages
        min_buses_per_garage: int = 1
    ):
        """
        Randomly selects garage nodes and assigns buses so that:
        - sum(buses) == total route demand
        - bus counts are reasonably balanced
        """

        G = self.main_graph
        total_demand = int(self.Routes_obj["total_demand"])

        if total_demand <= 0:
            raise ValueError("Total route demand must be > 0")

        # ---- choose garage nodes ----
        nodes = list(G.nodes())
        n_garages = max(1, int(len(nodes) * ratio))

        garage_nodes = sample(nodes, n_garages)

        # mark nodes in graph
        for n in nodes:
            G.nodes[n]["is_garage"] = False

        for n in garage_nodes:
            G.nodes[n]["is_garage"] = True

        # ---- distribute buses ----
        # start with even split
        base = total_demand // n_garages
        remainder = total_demand % n_garages

        buses = [base] * n_garages

        # spread remainder
        for i in range(remainder):
            buses[i] += 1

        # introduce randomness but keep balance
        for _ in range(n_garages * 2):
            i, j = sample(range(n_garages), 2)

            if buses[i] - buses[j] > max_diff and buses[i] > min_buses_per_garage:
                delta = rand_num(1, min(max_diff // 2, buses[i] - min_buses_per_garage))
                buses[i] -= delta
                buses[j] += delta

        # final safety normalization
        diff = max(buses) - min(buses)
        if diff > max_diff:
            avg = total_demand // n_garages
            buses = [avg] * n_garages
            for i in range(total_demand - avg * n_garages):
                buses[i] += 1

        # ---- store garages ----
        self.Garages = {
            garage_nodes[i]: buses[i]
            for i in range(n_garages)
        }

        return self.Garages

    
    @staticmethod
    def print_routes_sorted(R):
        edges = []

        # IMPORTANT: MultiGraph must use keys=True
        for u, v, key, data in R.edges(keys=True, data=True):
            edges.append((data["number"], u, v, data))

        edges.sort(key=lambda x: x[0])

        current = None
        for number, u, v, data in edges:
            if number != current:
                print(f"\n=== ROUTE {number} ===")
                current = number

            print(f"{u} -> {v}")

if __name__ == "__main__":
    G = nx.read_gexf('../data/map/graph_10nodes_100density.gexf')
    rm = RouteManager(G)
    
    R, res = rm.gen_routes(verbose=True)
    nx.write_gexf(R, "routes_.gexf")

    RouteManager.print_routes_sorted(R)
