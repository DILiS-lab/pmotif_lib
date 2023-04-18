"""Utilities to read and write edgelists in a gtrieScanner friendly format."""
from pathlib import Path

import networkx as nx


def write_shifted_edgelist(
    graph: nx.Graph, path: Path, reindex: bool = False, shift: int = 1
):
    """Writes the edgelist of a graph to a given path.
    Can reindex the given nodes, turning any node label to an integer representing the index of
    that node.
    Can apply a shift to node labels, if they are integers, increasing them by `shift`.
    Use reindex and shift to create edge lists with integer node labels above 0, as gtrieScanner
    can only handle such representation of edges."""
    if reindex:
        # Create node mapping
        node_mapping = {n: i for i, n in enumerate(graph.nodes)}
    else:
        node_mapping = dict(zip(graph.nodes, map(int, graph.nodes)))

    # Creates edge list lines in the form of `u v 1`
    # The `1` is necessary for gTrieScanner to function correctly, as it always expects a weight
    lines = [
        f"{node_mapping[u] + shift} {node_mapping[v] + shift} 1\n"
        for u, v in graph.edges()
    ]
    with open(path, "w", encoding="utf-8") as out:
        out.writelines(lines)


def read_edgelist(graph_edgelist: Path) -> nx.Graph:
    """Read an edgelist without data, creating an undirected simple graph with no self loops."""
    # Make sure network is in gTrie-readable format
    graph = nx.read_edgelist(
        str(graph_edgelist),
        data=False,
        create_using=nx.Graph,  # No repeated edges, no direction
    )
    graph.remove_edges_from(nx.selfloop_edges(graph))
    return graph
