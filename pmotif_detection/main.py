from os import makedirs
from pathlib import Path

import networkx as nx
from tqdm import tqdm

from pmotifs.PMotifGraph import PMotifGraph, PMotifGraphWithRandomization

from pmotifs.config import (
    GTRIESCANNER_EXECUTABLE,
    EXPERIMENT_OUT,
    DATASET_DIRECTORY,
)

from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from pmotifs.positional_metrics import calculate_metrics


def assert_validity(pmotif_graph: PMotifGraph):
    """Raises a ValueError of underlying graph is not valid for gtrieScanner input"""
    nx_graph = pmotif_graph.load_graph()

    if len(list(nx.selfloop_edges(nx_graph))) > 0:
        raise ValueError("Graph contains Self-Loops!")  # Asserts simple graph

    if min(map(int, nx_graph.nodes)) < 1:
        raise ValueError("Graph contains node ids below '1'!")  # Assert the lowest node index is >= 1


def process_graph(pmotif_graph: PMotifGraph, graphlet_size: int, check_validity: bool = True):
    if check_validity:
        assert_validity(pmotif_graph)

    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
        directed=False,
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )
    positional_metrics = calculate_metrics(pmotif_graph, graphlet_size)
    positional_metrics.save(pmotif_graph.get_positional_data_directory(graphlet_size))


def main(edgelist: Path, out: Path, graphlet_size: int, random_graphs: int = 0):

    pmotif_graph = PMotifGraph(edgelist, out)

    process_graph(
        pmotif_graph,
        graphlet_size,
    )

    if random_graphs > 0:
        randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(pmotif_graph, random_graphs)
        del pmotif_graph

        pbar_swapped_graphs = tqdm(
            randomized_pmotif_graph.swapped_graphs,
            desc="Processing swapped graphs",
            leave=True,
        )
        swapped_graph: PMotifGraph
        for swapped_graph in pbar_swapped_graphs:
            process_graph(swapped_graph, graphlet_size, check_validity=False)


if __name__ == "__main__":
    GRAPH_EDGELIST = DATASET_DIRECTORY / "yeastInter_st.txt"
    OUT = EXPERIMENT_OUT / "pmotif_detection"
    RANDOM_GRAPHS = 10
    GRAPHLET_SIZE = 3

    makedirs(OUT, exist_ok=True)

    main(GRAPH_EDGELIST, OUT, GRAPHLET_SIZE, RANDOM_GRAPHS)
