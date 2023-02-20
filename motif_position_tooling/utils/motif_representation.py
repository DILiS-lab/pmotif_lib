"""Utility Methods to transform motif ids into different representations"""

import networkx as nx


MOTIF_NAME_LOOKUP = {
    "011 101 110": "Triangle",
    "001 001 110": "3-Dash",
    "0111 1000 1000 1000": "Fork",
    "0110 1001 1000 0100": "4-Dash",
    "0111 1010 1100 1000": "Spoon",
    "0111 1011 1100 1100": "Crossed Square",
    "0111 1011 1101 1110": "Double Crossed Square",
    "0110 1001 1001 0110": "Square",
}


def motif_id_to_name(motif_id: str) -> str:
    return MOTIF_NAME_LOOKUP[motif_id]


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
