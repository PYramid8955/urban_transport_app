import json
import networkx as nx

def multigraph_to_cytoscape_json(R: nx.MultiGraph, save_path: str | None = None):

    cy_nodes = []
    cy_edges = []

    for node in R.nodes():
        cy_nodes.append({
            "data": {
                "id": node,
                "label": node
            }
        })

    for u, v, key, data in R.edges(keys=True, data=True):
        edge_id = f"{u}__{v}__{key}"

        cy_edges.append({
            "data": {
                "id": edge_id,
                "source": u,
                "target": v,
                # copy all edge attributes (route number, travel_time, etc.)
                **data
            }
        })

    cy_json = {
        "elements": {
            "nodes": cy_nodes,
            "edges": cy_edges
        }
    }

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cy_json, f, indent=2, ensure_ascii=False)

    return cy_json
