import argparse
import shutil
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
import time
import logging


def assert_validity(pmotif_graph: PMotifGraph):
    """Raises a ValueError of underlying graph is not valid for gtrieScanner input"""
    nx_graph = pmotif_graph.load_graph()

    if len(list(nx.selfloop_edges(nx_graph))) > 0:
        raise ValueError("Graph contains Self-Loops!")  # Asserts simple graph

    if min(map(int, nx_graph.nodes)) < 1:
        raise ValueError("Graph contains node ids below '1'!")  # Assert the lowest node index is >= 1


def process_graph(
    pmotif_graph: PMotifGraph,
    graphlet_size: int,
    metrics: List[PMetric.PMetric],
    check_validity: bool = True,
):
    if check_validity:
        assert_validity(pmotif_graph)

    start = time.time()
    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
        directed=False,
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )
    graphlet_runtime = time.time() - start

    if len(metrics) == 0:
        return

    start = time.time()
    calculate_metrics(pmotif_graph, graphlet_size, metrics, True)
    metric_runtime = time.time() - start
    return {
        "graphlet_runtime": graphlet_runtime,
        "metric_runtime": metric_runtime,
    }


def main(edgelist: Path, out: Path, graphlet_size: int, random_graphs: int = 0):
    degree = PDegree()
    anchor_node = PAnchorNodeDistance()
    graph_module_participation = PGraphModuleParticipation()

    pmotif_graph = PMotifGraph(edgelist, out)

    log_r = process_graph(
        pmotif_graph,
        graphlet_size,
        [degree, anchor_node, graph_module_participation],
    )
    for runtime_name, runtime in log_r.items():
        logger.info(f"{runtime_name}: {runtime}")

    start = time.time()
    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(pmotif_graph, random_graphs)
    random_creation_runtime = time.time() - start
    logger.info(f"Random Creation Runtime: {random_creation_runtime} (created {random_graphs})")

    del pmotif_graph

    pbar_swapped_graphs = tqdm(
        randomized_pmotif_graph.swapped_graphs,
        desc="Processing swapped graphs",
        leave=True,
    )
    swapped_graph: PMotifGraph
    for i, swapped_graph in enumerate(pbar_swapped_graphs):
        log_r = process_graph(
            swapped_graph,
            graphlet_size,
            [degree, anchor_node, graph_module_participation],
            check_validity=False,
        )
        for runtime_name, runtime in log_r.items():
            logger.info(f"Random {i}, {runtime_name}: {runtime}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--edgelist_name", required=True, type=str)
    parser.add_argument("--graphlet_size", required=True, type=int, default=3, choices=[3, 4])
    parser.add_argument("--benchmarking_run", required=True, type=int, choices=[1, 2, 3, 4, 5])

    args = parser.parse_args()

    GRAPH_EDGELIST = DATASET_DIRECTORY / args.edgelist_name
    OUT = EXPERIMENT_OUT / "benchmarking" / GRAPH_EDGELIST.stem
    GRAPHLET_SIZE = args.graphlet_size
    RANDOM_GRAPHS = 10
    BENCHMARKING_RUN = args.benchmarking_run

    makedirs(OUT, exist_ok=True)
    makedirs("benchmarking_logs", exist_ok=True)

    logging.basicConfig(
        filename=f"benchmarking_logs/{BENCHMARKING_RUN}_{GRAPH_EDGELIST.stem}_{GRAPHLET_SIZE}_{RANDOM_GRAPHS}.benchmark",
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
    )

    logger = logging.getLogger("benchmark")

    start = time.time()
    main(GRAPH_EDGELIST, OUT, GRAPHLET_SIZE, RANDOM_GRAPHS)
    total_runtime = time.time() - start
    logger.info(f"Total Runtime: {total_runtime}")
    shutil.rmtree(EXPERIMENT_OUT / "benchmarking")
