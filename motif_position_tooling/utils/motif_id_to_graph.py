import networkx as nx


def motif_id_to_graph(motif_id: str) -> nx.Graph:
    """motif_id is a k*k matrix where each row consists of either
    0 or 1, and rows a separated by space
    Example: 0110 1001 1000 0100"""
    rows = motif_id.split(" ")

    g = nx.Graph()
    for i in range(len(rows)):
        g.add_node(i)

    for i, row in enumerate(rows):
        for j, has_edge in enumerate(row):
            if has_edge == "1":
                g.add_edge(i, j)
    return g
