"""This utility takes a network and nodes (or supernodes)
and calculates various positional metrics for those inputs"""
from os import makedirs
from typing import (
    List,
    Dict,
)
from multiprocessing import Pool
from tqdm import tqdm
import networkx as nx
from pmotif_lib.graphlet_occurence import GraphletOccurrence
from pmotif_lib.p_motif_graph import PMotifGraph
from pmotif_lib.p_metric.p_metric import PMetric
from pmotif_lib.p_metric.p_metric_result import PMetricResult


def process_graphlet_occurrences(
    graph: nx.Graph,
    graphlet_occurrences: List[GraphletOccurrence],
    metrics: List[PMetric],
    workers: int = 1,
) -> List[PMetricResult]:
    """Calculate motif positional metrics"""

    result: Dict[str, Dict] = {m.name: {} for m in metrics}

    # Pre-Compute for metrics
    metric: PMetric
    for metric in tqdm(metrics, desc="Pre-computing metrics", leave=False):
        result[metric.name]["pre_compute"] = metric.pre_computation(graph)

    # Calculate metrics
    with Pool(processes=workers) as pool:
        for metric in tqdm(metrics, desc="Calculating metrics", leave=False):
            result[metric.name]["graphlet_metrics"] = []
            args = [
                (graph, g_oc.nodes, result[metric.name]["pre_compute"])
                for g_oc in graphlet_occurrences
            ]

            with tqdm(
                total=len(graphlet_occurrences),
                desc="Graphlet Occurrence Progress",
                leave=False,
            ) as pbar:
                for g_oc_result in pool.starmap(
                    metric.metric_calculation,
                    args,
                    chunksize=100,
                ):
                    result[metric.name]["graphlet_metrics"].append(g_oc_result)
                    pbar.update(1)

    return [
        PMetricResult(
            metric_name=m.name,
            pre_compute=result[m.name]["pre_compute"],
            graphlet_metrics=result[m.name]["graphlet_metrics"],
        )
        for m in metrics
    ]


def calculate_metrics(
    pmotif_graph: PMotifGraph,
    graphlet_size: int,
    metrics: List[PMetric],
    save_to_disk: bool = True,
    workers: int = 1,
) -> List[PMetricResult]:
    """When pointed to a graph and a motif file, unzips the motif file, reads the graphs,
     and calculates given positional metrics.
     Can save results directly to disk.
    Returns a list of the results as PMetricResult objects."""
    graph = nx.readwrite.edgelist.read_edgelist(
        pmotif_graph.get_graph_path(), data=False, create_using=nx.Graph
    )
    graphlet_occurrences: List[GraphletOccurrence] = pmotif_graph.load_graphlet_pos_zip(
        graphlet_size
    )

    metric_result_lookup = process_graphlet_occurrences(
        graph, graphlet_occurrences, metrics, workers=workers,
    )
    if save_to_disk:
        metric_output = pmotif_graph.get_pmetric_directory(graphlet_size)
        makedirs(metric_output)
        for metric_result in metric_result_lookup:
            metric_result.save_to_disk(metric_output)

    return metric_result_lookup
