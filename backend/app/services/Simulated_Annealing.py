import random
import math
import networkx as nx
from app.services import AStarTransport 

def simulated_annealing(G: nx.Graph, raw_route, temperature=100.0, max_iter=50, alpha=0.99):
    #solves the loop problem:
    G_alternative = G.copy()
    for i in range(len(raw_route) - 1):
        u = raw_route[i]
        v = raw_route[i + 1]
        
        if G_alternative.has_edge(u, v):
            G_alternative.remove_edge(u, v)
        if G_alternative.has_edge(v, u):   # even tho our graph isn't dirrected, I would still check this just in case
            G_alternative.remove_edge(v, u)

    a_star_solver = AStarTransport(G_alternative)  # A* instance to calculate routes between nodes that aren't dirrectly connecting, but avoiding loops

    # total route cost
    def total_cost(r):
        cost = 0
        actual_route = [r[0]]
        G_alternative_temp = G_alternative.copy()
        for i in range(len(r)-1):
            #prioritize structure over cost
            if G.has_edge(r[i], r[i+1]):
                cost += G[r[i]][r[i+1]]['weight']
                actual_route.append(r[i+1])
            else: 
                res = AStarTransport(G_alternative_temp).find_path(r[i], r[i+1])
                actual_route.extend(res['path'][1:])
                for x in res['path']:
                    if x not in r:
                        if G_alternative_temp.has_node(x):
                            G_alternative_temp.remove_node(x)
                        else: raise Exception("Somehow the node disappeared!")
                cost += res['total_time']
        
        return cost, actual_route

    current_route = raw_route[:]
    current_cost, actual_route = total_cost(current_route)
    best_actual_route = actual_route[:]
    best_route = current_route[:]
    best_cost = current_cost

    for iteration in range(max_iter):
        # small change: swap between 2 nodes (except first and last)
        if len(raw_route) > 3:  # check to have min 3 nodes for swap
            i, j = random.sample(range(1, len(raw_route)-1), 2)
            new_route = current_route[:]
            new_route[i], new_route[j] = new_route[j], new_route[i]

            new_cost, new_actual_route = total_cost(new_route)
            delta = new_cost - current_cost

            # accept if the new route is better or by probability
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_route = new_route
                current_cost = new_cost
                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost
                    best_actual_route = new_actual_route

        # cool the temp.
        temperature *= alpha

    return best_actual_route, best_cost, best_route
