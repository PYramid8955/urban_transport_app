from app.services import AStarTransport

def betweenness_centrality(G, astar, normalized=True, verbose = False):
    nodes = list(G.nodes())

    iter = 0
    expected = len(nodes) * (len(nodes)-1)/2
    
    BC = {v: 0 for v in nodes}

    # run for every ordered pair of nodes (s, t)
    for i in range(len(nodes)):
        s = nodes[i]
        for j in range(i + 1, len(nodes)):

            if verbose:
                print("\x1b[2J\x1b[H", end='')
                iter+=1
                print(f"{int(iter*100/expected)}%\nProcessed: {iter}\nFrom: {expected}")
            
            t = nodes[j]

            result = astar.find_path(s, t)
            path = result["path"]

            if len(path) <= 2:
                continue  # no intermediate nodes → no contribution

            # all intermediate nodes get +1
            intermediates = path[1:-1]
            for v in intermediates:
                BC[v] += 1

    # normalization (optional)
    if normalized:
        scale = 1 / ((len(nodes) - 1) * (len(nodes) - 2) / 2)
        for v in BC:
            BC[v] *= scale

    return BC
