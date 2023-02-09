"""Generates scale free graphs and randomizes them using edge swapping"""

from os import makedirs
from pathlib import Path
import argparse
from typing import List

import networkx as nx
from tqdm.contrib.concurrent import process_map

from motif_position_tooling.utils.edge_swapping import swap_edges_markov_chain
from motif_position_tooling.utils.motif_io import write_shifted_edgelist, MotifGraphWithRandomization

WORKERS = 8


# GENERATE GRAPHS
def _generate_graph(i, number_of_nodes, num_of_random_graphs, experiment_dir) -> MotifGraphWithRandomization:
    graph_name = "scale_free_graph.edgelist"

    makedirs(experiment_dir / str(i), exist_ok=True)
    # print(f"created {experiment_dir / str(i)}")
    # Scale Free Graph
    g = nx.scale_free_graph(
        n=number_of_nodes,
    )
    g = nx.Graph(g)
    g.remove_edges_from(nx.selfloop_edges(g))

    write_shifted_edgelist(g, experiment_dir / str(i) / graph_name, shift=1)
    # Generate random graphs
    edge_swapped_dir = experiment_dir / str(i) / MotifGraphWithRandomization.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME
    makedirs(edge_swapped_dir, exist_ok=True)

    for j in range(num_of_random_graphs):
        random_g = swap_edges_markov_chain(
            g.copy(),
            3,
            10,
        )
        write_shifted_edgelist(random_g, edge_swapped_dir / f"{j}_random.edgelist", shift=1)

    return MotifGraphWithRandomization(experiment_dir / str(i), graph_name)


def _generate_graphs_multiprocess_wrapper(args) -> MotifGraphWithRandomization:
    return _generate_graph(*args)


def generate_graphs(num_of_graphs, num_of_random_graphs, number_of_nodes, experiment_dir) -> List[MotifGraphWithRandomization]:
    # Generate args
    static_args = (number_of_nodes, num_of_random_graphs, experiment_dir.absolute())
    fn_args = [[i] + list(static_args) for i in range(num_of_graphs)]
    return process_map(
        _generate_graphs_multiprocess_wrapper,
        fn_args,
        max_workers=WORKERS,
        desc="Generating scale free graphs",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Scale Free Graph Generator",
        "Create scale free graphs and create randomized versions of those graphs"
    )

    parser.add_argument("num_of_graphs", type=int)
    parser.add_argument("num_of_random_graphs", type=int)
    parser.add_argument("n", type=int)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()

    generate_graphs(args.num_of_graphs, args.num_of_random_graphs, args.n, args.out_dir)
