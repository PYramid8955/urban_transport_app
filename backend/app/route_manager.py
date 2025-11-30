# here we use everything to create routes, edit the database and so on
from services import *
import networkx as nx
from math import ceil
from utils import multigraph_to_cytoscape_json

class RouteManager:
    # the desired route lenght in minutes (approx.), one way
    Routes = []

    def __init__(self, G: nx.Graph, route_length = 45, min_inter_station_time = 1, max_inter_station_time = 10):
        self.main_graph = G
        self.route_length = route_length
        self.min_inter_station_time = min_inter_station_time
        self.max_inter_station_time = max_inter_station_time

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


    def assign_routes(self, R: nx.MultiGraph, route, number, astar):
        for i in range(len(route)-1):
            path = [route[i], route[i+1]] if self.main_graph.has_edge(route[i], route[i+1]) else astar.find_path(route[i], route[i+1])['path']
            for j in range(len(path)-1):
                R.add_edge(path[j], path[j+1], number = number, travel_time = self.main_graph[path[j]][path[j+1]]['travel_time'], 
                        traffic = self.main_graph[path[j]][path[j+1]]['traffic'], weight = self.main_graph[path[j]][path[j+1]]['weight'])
        return [number, route]


    def gen_routes(self, verbose=False):
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

        # save attributes
        old_edges_attrs = []
        for key, attrs in R[u][v].items():
            old_edges_attrs.append(attrs.copy())

        # compute path
        temp_G = self.main_graph.copy()
        temp_G.remove_edge(u, v)

        astar = AStarTransport(temp_G)
        result = astar(u, v)
        path = result["path"]
        
        keys_to_remove = list(R[u][v].keys())
        for k in keys_to_remove:
            R.remove_edge(u, v, key=k)

        # add detour edges for each segment
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            for attrs in old_edges_attrs:
                R.add_edge(a, b, **attrs)

        return True


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
    

    # multigraph_to_cytoscape_json(R, "graph.json")
