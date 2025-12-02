# DEPRECATED (WON'T USE IT)

from pyvis.network import Network
import networkx as nx

def get_html_map_raw(path):
    G = nx.read_gexf(path)
    net = Network(notebook=False, width="100vw", height="100vh", bgcolor="#ffffff")
    net.from_nx(G)
    # net.write_html("graph.html", notebook=False, open_browser=True)
    return net.generate_html()

if __name__ == "__main__":
    print(get_html_map_raw('../data/map/graph_100nodes_30density.gexf'))