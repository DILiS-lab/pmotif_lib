from pathlib import Path

import networkx as nx


def write_shifted_edgelist(g: nx.Graph, path: Path, shift=1, reindex=False):
    node_mapping = dict(zip(g.nodes, g.nodes))
    if reindex:
        # Create node mapping
        node_mapping = {n: i for i, n in enumerate(g.nodes)}

    lines = [f"{node_mapping[u] + shift} {node_mapping[v] + shift}\n" for u, v in g.edges()]
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
