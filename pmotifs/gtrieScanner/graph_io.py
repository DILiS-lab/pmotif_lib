from pathlib import Path

import networkx as nx


def write_shifted_edgelist(g: nx.Graph, path: Path, shift=1, reindex=False):
    if reindex:
        # Create node mapping
        node_mapping = {n: i for i, n in enumerate(g.nodes)}
    else:
        node_mapping = dict(zip(g.nodes, map(int, g.nodes)))

    # Creates edge list lines in the form of `u v 1`
    # The `1` is necessary for gTrieScanner to function correctly, as it always expects a weight
    lines = [f"{node_mapping[u] + shift} {node_mapping[v] + shift} 1\n" for u, v in g.edges()]
    with open(path, "w") as out:
        out.writelines(lines)


def read_edgelist(graph_edgelist: Path) -> nx.Graph:
    # Make sure network is in gTrie-readable format
    g = nx.read_edgelist(
        str(graph_edgelist),
        data=False,
        create_using=nx.Graph,  # No repeated edges, no direction
    )
    g.remove_edges_from(nx.selfloop_edges(g))
    return g
