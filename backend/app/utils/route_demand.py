class RouteDemandCalculator:
    def __init__(self, graph):
        """
        graph: networkx graph
        """
        self.graph = graph

    def route_edges(self, route):
        """Convert node list to edge attribute dicts"""
        edges = []
        for u, v in zip(route[:-1], route[1:]):
            # For MultiGraph, take all parallel edges
            edge_data = self.graph.get_edge_data(u, v)

            if edge_data is None:
                raise ValueError(f"No edge between {u} and {v}")

            # normalize to list of attrs
            if isinstance(edge_data, dict) and 0 in edge_data:
                edges.extend(edge_data.values())
            else:
                edges.append(edge_data)

        return edges

    def bottleneck_demand(self, route):
        """
        Minimum traffic along the route
        """
        edges = self.route_edges(route)
        return min(edge["traffic"] for edge in edges)

    def average_demand(self, route):
        """
        Average traffic (less strict, optional)
        """
        edges = self.route_edges(route)
        return sum(edge["traffic"] for edge in edges) / len(edges)

    def weighted_demand(self, route):
        """
        Penalizes long routes:
        demand = bottleneck / number_of_edges
        """
        edges = self.route_edges(route)
        bottleneck = min(edge["traffic"] for edge in edges)
        return bottleneck / len(edges)