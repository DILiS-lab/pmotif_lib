# Reimplementation of the edgeswapping algo employed by gtrieScanner
# The networkx `connected_double_edge_swap` is also an option, but does not enable directed edges
# Or tries per edge
import networkx as nx
import random


def swap_edges_markov_chain(g: nx.Graph, num: int, tries: int):
    node_ids = list(g.nodes)

    for _ in range(num):
        for src in g.nodes:
            src_neighbors = list(g.neighbors(src))
            for dst in src_neighbors:
                for k in range(tries):
                    new_src = random.choice(node_ids)
                    new_src_neighbors = list(g.neighbors(new_src))

                    if len(new_src_neighbors) == 0:
                        continue
                    if not _is_valid_new_src(dst, g, new_src, src):
                        continue

                    new_dst = random.choice(new_src_neighbors)
                    if not _is_valid_new_dst(dst, g, new_dst, src):
                        continue

                    _swap_edges(g, src, dst, new_src, new_dst)
                    # Stop trying
                    break
    return g


def _swap_edges(g, src, dst, new_src, new_dst):
    g.remove_edge(src, dst)
    g.remove_edge(new_src, new_dst)
    g.add_edge(src, new_dst)
    g.add_edge(new_src, dst)


def _is_valid_new_dst(dst, g, new_dst, src):
    return src != new_dst and dst != new_dst and not g.has_edge(src, new_dst)


def _is_valid_new_src(dst, g, new_src, src):
    return src != new_src and dst != new_src and not g.has_edge(new_src, dst)
