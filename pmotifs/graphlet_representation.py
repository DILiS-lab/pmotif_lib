r"""Utility Methods to transform graphlets into different representations.
The two common representations are
1. Adj. Matrix String (by gTrieScanner)
A graphlet of size k is represented as k space-separated k-long binary strings
eg "011 101 110" for triangle, where each binary string represents a row in an adj. matrix
2. Given graphlet class name (own)
An arbitrarily chosen name for a graphlet class, such as "Triangle" and "Square":
   O  <-- Triangle  O -- O
 /  \               |    |
O -- O  Square -->  O -- O
"""
from typing import List

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


def graphlet_classes_from_size(graphlet_size: int) -> List[str]:
    """Return all graphlet classes of given size."""
    return [
        graphlet_class
        for graphlet_class in GRAPHLET_CLASS_NAME_LOOKUP
        if get_graphlet_size_from_class(graphlet_class) == graphlet_size
    ]


def get_graphlet_size_from_class(graphlet_class: str) -> int:
    """Determine the graphlet size from a graphlet class represented as adj. matrix string."""
    return len(graphlet_class.split(" ")[0])


def graphlet_class_to_name(graphlet_class: str) -> str:
    """Return the name of a given graphlet represented adj. matrix string."""
    return GRAPHLET_CLASS_NAME_LOOKUP[graphlet_class]


def graphlet_name_to_class(graphlet_class: str) -> str:
    """Return the adj. matrix string. of a given graphlet name."""
    return {v: k for k, v in GRAPHLET_CLASS_NAME_LOOKUP.items()}[graphlet_class]


def graphlet_class_to_graph(graphlet_class: str) -> nx.Graph:
    """motif_id is a k*k matrix where each row consists of either
    0 or 1, and rows a separated by space
    Example: 0110 1001 1000 0100"""
    rows = graphlet_class.split(" ")

    graph = nx.Graph()
    for i in range(len(rows)):
        graph.add_node(i)

    for i, row in enumerate(rows):
        for j, has_edge in enumerate(row):
            if has_edge == "1":
                graph.add_edge(i, j)
    return graph
