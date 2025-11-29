from services import AStarTransport

def betweenness_centrality(G, astar, normalized=True):
    nodes = list(G.nodes())
    BC = {v: 0 for v in nodes}

    # run for every ordered pair of nodes (s, t)
    for i in range(len(nodes)):
        s = nodes[i]
        for j in range(i + 1, len(nodes)):
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
