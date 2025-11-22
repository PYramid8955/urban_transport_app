import random
import math
from A_star import AStarTransport 

def simulated_annealing(G, raw_route, temperature=100.0, max_iter=50, alpha=0.99):
   
    a_star_solver = AStarTransport(G)  # instanțiem A* pentru calculul segmentelor

    # Funcție pentru costul total al rutei
    def total_cost(r):
        cost = 0
        for i in range(len(r)-1):
            segment = a_star_solver.find_path(r[i], r[i+1])
            cost += segment['total_time']
        return cost

    current_route = raw_route[:]  # ruta curentă
    current_cost = total_cost(current_route)
    best_route = current_route[:]
    best_cost = current_cost

    for iteration in range(max_iter):
        # Facem o mică schimbare: swap între două noduri (excluzând primul și ultimul)
        if len(raw_route) > 2:  # verificăm să avem minim 3 noduri pentru swap
            i, j = random.sample(range(1, len(raw_route)-1), 2)
            new_route = current_route[:]
            new_route[i], new_route[j] = new_route[j], new_route[i]

            new_cost = total_cost(new_route)
            delta = new_cost - current_cost

            # Acceptăm ruta nouă dacă e mai bună sau probabilistic
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_route = new_route
                current_cost = new_cost
                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost

        # Răcim temperatura
        temperature *= alpha

    return best_route, best_cost
