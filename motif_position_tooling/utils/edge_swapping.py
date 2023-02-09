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
                found = False
                for k in range(tries):
                    new_src = random.choice(node_ids)
                    new_src_neighbors = list(g.neighbors(new_src))
                    if len(new_src_neighbors) == 0:
                        continue
                    if src == new_src or dst == new_src or g.has_edge(new_src, dst):
                        # New src is either src or dst or already connected to dst
                        continue
                    new_dst = random.choice(new_src_neighbors)
                    if src == new_dst or dst == new_dst or g.has_edge(src, new_dst):
                        # New dst is either src or dst or already connected by src
                        continue
                    found = True
                    break
                if found:
                    # Did at least once not abort search loop
                    # Found suitable swapping partners
                    g.remove_edge(src, dst)
                    g.remove_edge(new_src, new_dst)

                    g.add_edge(src, new_dst)
                    g.add_edge(new_src, dst)
    return g
