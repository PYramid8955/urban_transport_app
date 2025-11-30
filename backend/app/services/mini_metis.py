import networkx as nx
import random
from collections import defaultdict
from models import BucketQueue

# very small constant that we'll use
EPS = 1e-9

def ensure_undirected(G):
    return G.to_undirected() if G.is_directed() else G.copy()

def preprocess_invert_edge_weights(G, cost_key="weight", sim_key="w", scale=1.0):
    for u, v, data in G.edges(data=True):
        cost = float(data.get(cost_key, 1.0))
        if cost <= 0: 
            cost = EPS
        sim = 1.0 / cost
        data[sim_key] = sim * scale

def edge_sim(G, u, v, sim_key="w"):
    return float(G[u][v].get(sim_key, 1.0))

def heavy_edge_matching_coarsen(G, min_coarse_size=50, sim_key="w", seed=None):
    if seed is not None:
        random.seed(seed)

    G = ensure_undirected(G)
    nodes = list(G.nodes())
    
    # edge cases
    if len(nodes) == 0:
        return G.copy(), {}
    if len(nodes) == 1:
        mapping = {nodes[0]: 0}
        Gc = nx.Graph()
        Gc.add_node(0, members=[nodes[0]])
        return Gc, mapping
        
    random.shuffle(nodes)
    matched = set()
    mapping = {}
    super_id = 0

    # try to match each node with its best unmatched neighbor for the first pass
    for u in nodes:
        if u in matched:
            continue

        best_v = None
        best_sim = -1.0
        for v in G.neighbors(u):
            if v not in matched and v != u:
                s = edge_sim(G, u, v, sim_key)
                if s > best_sim:
                    best_sim = s
                    best_v = v

        if best_v is not None:
            mapping[u] = super_id
            mapping[best_v] = super_id
            matched.add(u)
            matched.add(best_v)
            super_id += 1
        else:
            mapping[u] = super_id
            matched.add(u)
            super_id += 1

        # stop when we reach target coarse size
        if super_id >= min_coarse_size:
            break

    # handle any remaining unmatched nodes
    for node in nodes:
        if node not in mapping:
            mapping[node] = super_id
            super_id += 1

    # build coarse graph
    Gc = nx.Graph()
    members = defaultdict(list)
    for n, s in mapping.items():
        members[s].append(n)
    
    for s, mem_list in members.items():
        Gc.add_node(s, members=mem_list)

    edge_dict = defaultdict(float)
    for u, v, data in G.edges(data=True):
        su = mapping[u]
        sv = mapping[v]
        if su == sv:
            continue
        key = (min(su, sv), max(su, sv))
        edge_dict[key] += float(data.get(sim_key, 1.0))

    for (su, sv), w in edge_dict.items():
        Gc.add_edge(su, sv, w=w)

    return Gc, mapping

def greedy_initial_bisection(G, sim_key="w"):
    nodes = list(G.nodes())
    
    if len(nodes) == 0:
        return {}
    if len(nodes) == 1:
        return {nodes[0]: 0}
    
    # more connected nodes first
    deg_dict = {}
    for node in nodes:
        deg = 0.0
        for neighbor in G.neighbors(node):
            deg += G[node][neighbor].get(sim_key, 1.0)
        deg_dict[node] = deg
    
    nodes_sorted = sorted(nodes, key=lambda x: deg_dict[x], reverse=True)
    
    part = {}
    count_0, count_1 = 0, 0
    target = len(nodes) / 2
    
    for node in nodes_sorted:
        if count_0 <= count_1 and count_0 < target:
            part[node] = 0
            count_0 += 1
        else:
            part[node] = 1
            count_1 += 1
            
    return part

def cut_size(G, part, sim_key="w"):
    cut = 0.0
    for u, v, data in G.edges(data=True):
        if part.get(u) != part.get(v):
            cut += data.get(sim_key, 1.0)
    return cut

# Fiduccia–Mattheyses refinement with efficient bucket queues.
# balance_tol is tolerated fraction (e.g., 0.03 => +-3%).
def fm_bisection_refine(G, part, sim_key="w", max_passes=10, balance_tol=0.03):
    N = G.number_of_nodes()
    if N == 0:
        return part
        
    ideal = N / 2.0
    min_allowed = max(1, int((1.0 - balance_tol) * ideal))  # ensure at least 1 node per part
    max_allowed = min(N-1, int((1.0 + balance_tol) * ideal))  # ensure at least 1 node per part
    
    gains = {}
    buckets_0 = BucketQueue()
    buckets_1 = BucketQueue()
    
    def compute_gain(node, current_partition):
        p = current_partition[node]
        external, internal = 0.0, 0.0
        for neighbor in G.neighbors(node):
            w = float(G[node][neighbor].get(sim_key, 1.0))
            if current_partition[neighbor] == p:
                internal += w
            else:
                external += w
        return external - internal
    
    # initialize all gains
    for node in G.nodes():
        gain = compute_gain(node, part)
        gains[node] = gain
        if part[node] == 0:
            buckets_0.insert(gain, node)
        else:
            buckets_1.insert(gain, node)
    
    locked = set()
    best_part = part.copy()
    best_cut = cut_size(G, part, sim_key)
    
    for pass_num in range(max_passes):
        current_part = part.copy()
        current_cut = best_cut
        count_0 = sum(1 for n in G.nodes() if current_part[n] == 0)
        count_1 = N - count_0
        
        # create temporary bucket queues for this pass
        temp_buckets_0 = BucketQueue()
        temp_buckets_1 = BucketQueue()
        for node in G.nodes():
            if current_part[node] == 0:
                temp_buckets_0.insert(gains[node], node)
            else:
                temp_buckets_1.insert(gains[node], node)
        
        move_sequence = []
        improved = False
        
        # try to move N nodes (one pass)
        for move_idx in range(N):
            # find best movable node
            candidate = None
            from_part = None
            
            # part 0 -> part 1
            while not temp_buckets_0.is_empty() and candidate is None:
                gain, node = temp_buckets_0.pop_max()
                if node in locked:
                    continue
                if count_0 - 1 >= min_allowed and count_1 + 1 <= max_allowed:
                    candidate = node
                    from_part = 0
                else:
                    temp_buckets_0.insert(gain, node)
                    break
            
            while not temp_buckets_1.is_empty() and candidate is None:
                gain, node = temp_buckets_1.pop_max()
                if node in locked:
                    continue
                if count_1 - 1 >= min_allowed and count_0 + 1 <= max_allowed:
                    candidate = node
                    from_part = 1
                else:
                    temp_buckets_1.insert(gain, node)
                    break
            
            if candidate is None:
                break  # no valid moves remain
                
            old_part = from_part
            new_part = 1 - old_part
            move_gain = gains[candidate]
            
            current_part[candidate] = new_part
            locked.add(candidate)
            move_sequence.append((candidate, old_part, new_part, move_gain))
            
            if old_part == 0:
                count_0 -= 1
                count_1 += 1
            else:
                count_1 -= 1
                count_0 += 1
                
            current_cut -= move_gain
            
            for neighbor in G.neighbors(candidate):
                if neighbor in locked:
                    continue
                    
                old_gain = gains[neighbor]
                new_gain = compute_gain(neighbor, current_part)
                gains[neighbor] = new_gain
                
                if current_part[neighbor] == 0:
                    temp_buckets_0.remove(old_gain, neighbor)
                    temp_buckets_0.insert(new_gain, neighbor)
                else:
                    temp_buckets_1.remove(old_gain, neighbor)
                    temp_buckets_1.insert(new_gain, neighbor)
            
            if current_cut < best_cut:
                best_cut = current_cut
                best_part = current_part.copy()
                improved = True
        
        if not improved and pass_num > 0:
            break
            
        part = best_part.copy()
        locked.clear()
        
        for node in G.nodes():
            gains[node] = compute_gain(node, part)
            
    return best_part

def project_partition(fine_nodes, coarse_map, coarse_part):
    part = {}
    for n in fine_nodes:
        c = coarse_map[n]
        part[n] = coarse_part.get(c, 0)  # Default to 0 if not found
    return part

# Multilevel bisection using coarsening and refinement.
def multilevel_bisection(G_orig, sim_key="w", max_levels=20, min_coarse_size=20, balance_tol=0.03):
    G0 = ensure_undirected(G_orig)
    
    # handle trivial edge cases
    if G0.number_of_nodes() <= 1:
        return {node: 0 for node in G0.nodes()}
    
    graphs = [G0]
    mappings = []
    
    current_G = G0
    while current_G.number_of_nodes() > min_coarse_size and len(graphs) < max_levels:
        Gc, mapping = heavy_edge_matching_coarsen(current_G, min_coarse_size=min_coarse_size, sim_key=sim_key)
        
        if Gc.number_of_nodes() >= current_G.number_of_nodes() * 0.8:
            break
            
        graphs.append(Gc)
        mappings.append(mapping)
        current_G = Gc

    G_coarsest = graphs[-1]
    coarse_part = greedy_initial_bisection(G_coarsest, sim_key)
    coarse_part = fm_bisection_refine(G_coarsest, coarse_part, sim_key=sim_key, balance_tol=balance_tol)

    # uncoarsen and refine
    part = coarse_part
    for level in range(len(mappings)-1, -1, -1):
        # project to finer level
        part = project_partition(graphs[level].nodes(), mappings[level], part)
        # refine at this level
        part = fm_bisection_refine(graphs[level], part, sim_key=sim_key, balance_tol=balance_tol)
    
    return part

def recursive_k_partition(G, k, sim_key="w", balance_tol=0.03):
    if k <= 1:
        return {n: 0 for n in G.nodes()}
    
    # handle case where k > number of nodes
    if k > G.number_of_nodes():
        k = G.number_of_nodes()
    
    def split_subgraph(node_list, parts_to_make, offset, parent_balance_tol):
        if len(node_list) == 0:
            return {}
            
        if parts_to_make == 1:
            return {n: offset for n in node_list}
            
        subG = G.subgraph(node_list).copy()
        
        current_balance_tol = min(0.5, parent_balance_tol * 1.1)  # Cap at 50%
        
        bis_part = multilevel_bisection(subG, sim_key=sim_key, balance_tol=current_balance_tol)
        
        left_nodes = [n for n, p in bis_part.items() if p == 0]
        right_nodes = [n for n, p in bis_part.items() if p == 1]
        
        left_parts = parts_to_make // 2
        right_parts = parts_to_make - left_parts
        
        left_assign = split_subgraph(left_nodes, left_parts, offset, current_balance_tol)
        right_assign = split_subgraph(right_nodes, right_parts, offset + left_parts, current_balance_tol)
        
        left_assign.update(right_assign)
        return left_assign
    
    return split_subgraph(list(G.nodes()), k, 0, balance_tol)

# public api
def metis_partition(G_in, k=4, balance_tol=0.03, cost_key="weight", sim_key="w", scale=1.0):
    if k < 1:
        raise ValueError("k must be at least 1")
        
    G = ensure_undirected(G_in).copy()
    
    # handle empty graph
    if G.number_of_nodes() == 0:
        return {}, {}
    
    preprocess_invert_edge_weights(G, cost_key=cost_key, sim_key=sim_key, scale=scale)
    parts = recursive_k_partition(G, k, sim_key=sim_key, balance_tol=balance_tol)
    clusters = defaultdict(list)
    for n, pid in parts.items():
        clusters[pid].append(n)
    return parts, dict(clusters)

if __name__ == "__main__":
    import random
    for size in [10, 100, 500]:
        print(f"\nTesting with {size} nodes:")
        G = nx.erdos_renyi_graph(size, 0.1, seed=42)
        for u, v in G.edges():
            distance = random.uniform(1.0, 10.0)
            traffic = random.uniform(1.0, 10.0)
            cost = distance / (traffic ** 0.5)
            G[u][v]['weight'] = cost
            
        parts, clusters = metis_partition(G, k=4, balance_tol=0.05)
        print("Cluster sizes:", {pid: len(nodes) for pid, nodes in clusters.items()})
        print("Total cut size:", cut_size(G, parts, sim_key="w"))
        print(clusters)
        print(parts)
        
        # verify all nodes are assigned
        all_assigned = len(parts) == G.number_of_nodes()
        print(f"All nodes assigned: {all_assigned}")