# here we use everything to create routes, edit the database and so on
from services import *
import networkx as nx
from math import ceil

# the desired route lenght in minutes (approx.), one way
route_length = 45

def compute_hub_graph(hubs, astar):
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
            dist = res['total_time']
            avg_time += dist

            G.add_edge(u, v, weight=dist)

    avg_time /= (len(hub_nodes) * (len(hub_nodes) - 1)) / 2
    return G, avg_time


def assign_routes(R: nx.Graph, route, number):
    for i in range(len(route)-1):
        R.add_edge(route[i], route[i+1], number = number)
    return {number: route}


def gen_routes(G: nx.Graph, min_inter_station_time = 1, max_inter_station_time = 10):
    R = nx.Graph() # routes-only graph
    R.add_nodes_from(G.nodes())

    astarG = AStarTransport(G)

    res = {'betweeness_centrality': betweenness_centrality(G, astarG), 'routes': []}
    print('Generated scores for all nodes with BC.')

    working_G = G

    avg_time = (min_inter_station_time+max_inter_station_time)/2
    while True:
        total_stations = working_G.number_of_nodes()
        stations_per_route = route_length/avg_time + 1
        if (int(stations_per_route) == 1): stations_per_route+=1
        k_clusters = ceil(total_stations/stations_per_route)
        #1. clustering
        parts, clusters = metis_partition(working_G, k=k_clusters, balance_tol=0.05, scale=100)
        #2. get routes
        for i, cluster in clusters.items():
            route, cost = simulated_annealing(G, cluster)
            res['routes'].append(assign_routes(R, route, i + len(res['routes'])))
            print(f"Used SA to generate route {len(res['routes'])} with cost {cost}.")

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
        working_G, avg_time = compute_hub_graph(hubs_list, astarG)

        print('Computed hub graph successfully! Now running the whole thing again, but on the hubs')

if __name__ == "__main__":
    G = nx.read_gexf('../data/map/graph_100nodes_30density.gexf')
    R, res = gen_routes(G)
    from pyvis.network import Network
    net = Network(notebook=False, width="100vw", height="100vh", bgcolor="#ffffff")
    net.from_nx(R)
    # net.write_html("graph.html", notebook=False, open_browser=True)
    net.write_html("routes_.html")