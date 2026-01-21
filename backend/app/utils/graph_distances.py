import networkx as nx

def compute_garage_distances(G, garages, weight="travel_time"):
    """
    Returns:
    { garage_node: { target_node: distance } }
    """
    distances = {}
    for g in garages:
        distances[g] = nx.single_source_dijkstra_path_length(G, g, weight=weight)
    return distances
