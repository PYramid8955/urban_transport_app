from collections import deque
import math

def spfa(graph, source):
    """
    graph: adjacency list of FlowEdge
    returns: (dist, parent)
    """
    n = len(graph)
    dist = [math.inf] * n
    in_queue = [False] * n
    parent = [(-1, -1)] * n  # (prev_node, edge_index)

    dist[source] = 0
    q = deque([source])
    in_queue[source] = True

    while q:
        u = q.popleft()
        in_queue[u] = False

        for i, e in enumerate(graph[u]):
            if e.capacity > 0 and dist[u] + e.cost < dist[e.to]:
                dist[e.to] = dist[u] + e.cost
                parent[e.to] = (u, i)
                if not in_queue[e.to]:
                    q.append(e.to)
                    in_queue[e.to] = True

    return dist, parent
