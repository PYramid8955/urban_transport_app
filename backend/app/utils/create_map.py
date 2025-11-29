import networkx as nx
import os
import random
import math

# creates a random connected graph with station names instead of numbers.
def create_map(nodes, density, path='', station_names=None, 
               min_travel_time=1, max_travel_time=60,
               min_traffic=10, max_traffic=1000):
    if nodes < 1:
        raise ValueError("Number of nodes must be at least 1")
    if not 0 <= density <= 1:
        raise ValueError("Density must be between 0 and 1")
    if min_travel_time <= 0 or max_travel_time <= 0:
        raise ValueError("Travel times must be positive")
    if min_traffic <= 0 or max_traffic <= 0:
        raise ValueError("Traffic values must be positive")
    
    if station_names is None:
        station_names = [f"Station_{i}" for i in range(nodes)]
    elif len(station_names) < nodes:
        raise ValueError(f"Not enough station names provided. Need {nodes}, but got {len(station_names)}")
    
    selected_names = random.sample(station_names, nodes)
    
    # create a connected graph using a random tree as base
    G = nx.random_labeled_tree(nodes, seed=random.randint(0, 1000))
    
    # add attributes to edges in the initial tree
    for u, v in G.edges():
        travel_time = random.randint(min_travel_time, max_travel_time)
        traffic = random.randint(min_traffic, max_traffic)
        weight = travel_time / math.sqrt(traffic)
        
        G[u][v]['travel_time'] = travel_time
        G[u][v]['traffic'] = traffic
        G[u][v]['weight'] = weight
    
    # add more edges based on density
    max_possible_edges = nodes * (nodes - 1) // 2
    current_edges = nodes - 1 
    target_edges = int(density * max_possible_edges)
    
    # add random edges until we reach the target density
    while current_edges < target_edges and current_edges < max_possible_edges:
        u = random.randint(0, nodes - 1)
        v = random.randint(0, nodes - 1)
        
        if u != v and not G.has_edge(u, v):
            travel_time = random.randint(min_travel_time, max_travel_time)
            traffic = random.randint(min_traffic, max_traffic)
            weight = travel_time / math.sqrt(traffic)
            
            G.add_edge(u, v, travel_time=travel_time, traffic=traffic, weight=weight)
            current_edges += 1
    
    # relabel nodes from numbers to station names
    mapping = {i: selected_names[i] for i in range(nodes)}
    G = nx.relabel_nodes(G, mapping)
    
    # save to GEXF file at path
    if path:
        os.makedirs(path, exist_ok=True)
        
        filename = f"graph_{nodes}nodes_{int(density*100)}density.gexf"
        filepath = os.path.join(path, filename)
        
        nx.write_gexf(G, filepath)
        print(f"Graph saved to: {filepath}")
    
    return G

def print_graph_info(G):
    """Print detailed information about the graph and its edges"""
    print(f"\nGraph info:")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Connected: {nx.is_connected(G)}")
    
    print(f"\nEdge details:")
    for u, v, data in G.edges(data=True):
        print(f"{u} -- {v}: travel_time={data['travel_time']} min, "
              f"traffic={data['traffic']} passengers, weight={data['weight']:.3f}")

# for testing:
if __name__ == "__main__":
    from json import loads
    with open('../data/station_names.json', 'r') as f: 
        stations = loads(f.read())['stations']

    # create a graph with custom travel times and traffic
    G = create_map(
        100, 
        0.3, 
        '../data/map', 
        stations,
        min_travel_time=1,    # 5 minutes minimum travel time
        max_travel_time=10,   # 45 minutes maximum travel time  
        min_traffic=10,       # 50 passengers minimum
        max_traffic=100       # 500 passengers maximum
    )
    
    # print detailed graph info
    print_graph_info(G)
    
    # create another graph with different parameters
    print("\n" + "="*50)
    G2 = create_map(
        5, 
        0.5,
        min_travel_time=2,
        max_travel_time=30,
        min_traffic=100,
        max_traffic=1000
    )
    
    print_graph_info(G2)