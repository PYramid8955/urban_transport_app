import networkx as nx
import os
import random

def create_map(nodes, density, path='', station_names=None):
    """
    Creates a random connected graph with station names instead of numbers.
    
    Args:
        nodes (int): Number of nodes in the graph
        density (float): Edge density between 0 and 1
        path (str): Folder path where the GEXF file will be saved
        station_names (list): List of station names to use
    
    Returns:
        nx.Graph: The created graph object with station names
    """
    # Validate inputs
    if nodes < 1:
        raise ValueError("Number of nodes must be at least 1")
    if not 0 <= density <= 1:
        raise ValueError("Density must be between 0 and 1")
    
    # Handle station names
    if station_names is None:
        # Default station names if none provided
        station_names = [f"Station_{i}" for i in range(nodes)]
    elif len(station_names) < nodes:
        raise ValueError(f"Not enough station names provided. Need {nodes}, but got {len(station_names)}")
    
    # Randomly select unique station names
    selected_names = random.sample(station_names, nodes)
    
    # Create a connected graph using a random tree as base
    G = nx.random_tree(nodes, seed=random.randint(0, 1000))
    
    # Add more edges based on density
    max_possible_edges = nodes * (nodes - 1) // 2
    current_edges = nodes - 1 
    target_edges = int(density * max_possible_edges)
    
    # Add random edges until we reach the target density
    while current_edges < target_edges and current_edges < max_possible_edges:
        u = random.randint(0, nodes - 1)
        v = random.randint(0, nodes - 1)
        
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v)
            current_edges += 1
    
    # Relabel nodes from numbers to station names
    mapping = {i: selected_names[i] for i in range(nodes)}
    G = nx.relabel_nodes(G, mapping)
    
    # Save to GEXF file at path
    if path:
        os.makedirs(path, exist_ok=True)
        
        filename = f"graph_{nodes}nodes_{int(density*100)}density.gexf"
        filepath = os.path.join(path, filename)
        
        nx.write_gexf(G, filepath)
        print(f"Graph saved to: {filepath}")
    
    return G

if __name__ == "__main__":
    from json import loads
    with open('./station_names.json', 'r') as f: stations = loads(f.read())['stations']

    # Create a graph with 10 nodes and 0.3 density, save to 'graphs' folder
    G = create_map(20, 0.3, 'data/map', stations)
    
    # Print graph info
    print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    print(f"Connected: {nx.is_connected(G)}")
    
    # Create another graph without saving
    G2 = create_map(5, 0.5)
    print(f"Second graph: {G2.number_of_nodes()} nodes, {G2.number_of_edges()} edges")