"""Null models to randomize input graph."""
import random
import networkx as nx


def swap_edges_markov_chain(graph: nx.Graph, num: int, tries: int):
    """Classic markov style edge swapping algorithm.
    Reimplementation of the edgeswapping algo employed by gtrieScanner."""
    node_ids = list(graph.nodes)

    for _ in range(num):
        for src in graph.nodes:
            src_neighbors = list(graph.neighbors(src))
            for dst in src_neighbors:
                for _ in range(tries):
                    new_src = random.choice(node_ids)
                    new_src_neighbors = list(graph.neighbors(new_src))

                    if len(new_src_neighbors) == 0:
                        continue
                    if not _is_valid_new_src(dst, graph, new_src, src):
                        continue

                    new_dst = random.choice(new_src_neighbors)
                    if not _is_valid_new_dst(dst, graph, new_dst, src):
                        continue

                    _swap_edges(graph, src, dst, new_src, new_dst)
                    # Stop trying
                    break
    return graph


def _swap_edges(graph, src, dst, new_src, new_dst):
    """Swaps the edges between src-dst and new_src-new_dst in graph."""
    graph.remove_edge(src, dst)
    graph.remove_edge(new_src, new_dst)
    graph.add_edge(src, new_dst)
    graph.add_edge(new_src, dst)


def _is_valid_new_dst(dst, graph, new_dst, src):
    """Checks whether a new destination for an edge is
    not the same as the old source,
    not the same as the old destination,
    and whether src-new_dst is not already an edge in graph."""
    return src != new_dst and dst != new_dst and not graph.has_edge(src, new_dst)


def _is_valid_new_src(dst, graph, new_src, src):
    """Checks whether a new source for an edge is not the same as the old source or old destination
    and whether new_src-dst is not already an edge in graph."""
    return src != new_src and dst != new_src and not graph.has_edge(new_src, dst)
