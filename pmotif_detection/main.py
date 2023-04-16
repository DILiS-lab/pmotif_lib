import argparse
from os import makedirs
from pathlib import Path
from typing import List

import networkx as nx
from tqdm import tqdm

import pmotifs.pMetrics.PMetric as PMetric
from pmotifs.PMotifGraph import PMotifGraph, PMotifGraphWithRandomization
from pmotifs.config import (
    GTRIESCANNER_EXECUTABLE,
    EXPERIMENT_OUT,
    DATASET_DIRECTORY,
)
from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from pmotifs.pMetrics.PAnchorNodeDistance import PAnchorNodeDistance
from pmotifs.pMetrics.PDegree import PDegree
from pmotifs.pMetrics.PGraphModuleParticipation import PGraphModuleParticipation
from pmotifs.positional_metrics import calculate_metrics


def assert_validity(pmotif_graph: PMotifGraph):
    """Raises a ValueError of underlying graph is not valid for gtrieScanner input"""
    nx_graph = pmotif_graph.load_graph()

    if len(list(nx.selfloop_edges(nx_graph))) > 0:
        raise ValueError("Graph contains Self-Loops!")  # Asserts simple graph

    if min(map(int, nx_graph.nodes)) < 1:
        raise ValueError(
            "Graph contains node ids below '1'!"
        )  # Assert the lowest node index is >= 1


def process_graph(
    pmotif_graph: PMotifGraph,
    graphlet_size: int,
    metrics: List[PMetric.PMetric],
    check_validity: bool = True,
):
    if check_validity:
        assert_validity(pmotif_graph)

    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
        directed=False,
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )

    if len(metrics) == 0:
        return

    calculate_metrics(pmotif_graph, graphlet_size, metrics, True)


def main(edgelist: Path, out: Path, graphlet_size: int, random_graphs: int = 0):
    degree = PDegree()
    anchor_node = PAnchorNodeDistance()
    graph_module_participation = PGraphModuleParticipation()

    pmotif_graph = PMotifGraph(edgelist, out)

    process_graph(
        pmotif_graph,
        graphlet_size,
        [degree, anchor_node, graph_module_participation],
    )

    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(
        pmotif_graph, random_graphs
    )
    del pmotif_graph

    pbar_swapped_graphs = tqdm(
        randomized_pmotif_graph.swapped_graphs,
        desc="Processing swapped graphs",
        leave=True,
    )
    swapped_graph: PMotifGraph
    for swapped_graph in pbar_swapped_graphs:
        process_graph(
            swapped_graph,
            graphlet_size,
            [degree, anchor_node, graph_module_participation],
            check_validity=False,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--edgelist_name", required=True, type=str)
    parser.add_argument(
        "--graphlet_size", required=True, type=int, default=3, choices=[3, 4]
    )
    parser.add_argument("--random_graphs", required=False, type=int, default=0)

    args = parser.parse_args()

    GRAPH_EDGELIST = DATASET_DIRECTORY / args.edgelist_name
    OUT = EXPERIMENT_OUT / GRAPH_EDGELIST.stem
    GRAPHLET_SIZE = args.graphlet_size
    RANDOM_GRAPHS = args.random_graphs

    makedirs(OUT, exist_ok=True)

    main(GRAPH_EDGELIST, OUT, GRAPHLET_SIZE, RANDOM_GRAPHS)
