import heapq
#TODO
class AStarTransport:
    def __init__(self, graph, heuristic_func=None):
        
        self.graph = graph
        self.heuristic_func = heuristic_func if heuristic_func else (lambda n, end: 0)

    def find_path(self, start_node, end_node, traffic_weights=None, max_transfers=None):
       
        open_set = []
        heapq.heappush(open_set, (0, start_node, [start_node], 0))  
        g_scores = {start_node: 0}
        transfers_dict = {start_node: 0}

        while open_set:
            f_score, current, path, transfers = heapq.heappop(open_set)

            if current == end_node:
                return {
                    'path': path,
                    'total_time': g_scores[current],
                    'num_transfers': transfers
                }

            for neighbor, base_cost in self.graph.get(current, {}).items():
               
                traffic_cost = traffic_weights.get((current, neighbor), 0) if traffic_weights else 0
                tentative_g = g_scores[current] + base_cost + traffic_cost

               
                new_transfers = transfers
                if len(path) > 1 and path[-2] != current:
                    new_transfers += 1
                    tentative_g += 5  

               
                if max_transfers is not None and new_transfers > max_transfers:
                    continue

                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    transfers_dict[neighbor] = new_transfers
                    f_score_neighbor = tentative_g + self.heuristic_func(neighbor, end_node)
                    heapq.heappush(open_set, (f_score_neighbor, neighbor, path + [neighbor], new_transfers))

       
        return {'path': [], 'total_time': float('inf'), 'num_transfers': 0}
