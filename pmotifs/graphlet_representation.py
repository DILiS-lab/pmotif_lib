"""Utility Methods to transform motif ids into different representations"""

import networkx as nx


GRAPHLET_CLASS_NAME_LOOKUP = {
    "011 101 110": "Triangle",
    "011 100 100": "3-Dash",
    "0110 1001 1000 0100": "4-Dash",
    "0111 1000 1000 1000": "Fork",
    "0111 1010 1100 1000": "Spoon",
    "0110 1001 1001 0110": "Square",
    "0111 1011 1100 1100": "Crossed Square",
    "0111 1011 1101 1110": "Double Crossed Square",
}


def get_graphlet_size_from_class(graphlet_class: str) -> int:
    return len(graphlet_class.split(" ")[0])


def graphlet_class_to_name(graphlet_class: str) -> str:
    return GRAPHLET_CLASS_NAME_LOOKUP[graphlet_class]


def graphlet_name_to_class(graphlet_class: str) -> str:
    return {v: k for k, v in GRAPHLET_CLASS_NAME_LOOKUP.items()}[graphlet_class]


def graphlet_class_to_graph(graphlet_class: str) -> nx.Graph:
    """motif_id is a k*k matrix where each row consists of either
    0 or 1, and rows a separated by space
    Example: 0110 1001 1000 0100"""
    rows = graphlet_class.split(" ")

    g = nx.Graph()
    for i in range(len(rows)):
        g.add_node(i)

    for i, row in enumerate(rows):
        for j, has_edge in enumerate(row):
            if has_edge == "1":
                g.add_edge(i, j)
    return g
