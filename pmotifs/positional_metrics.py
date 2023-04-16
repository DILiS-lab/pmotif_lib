"""This utility takes a network and nodes (or supernodes)
and calculates various positional metrics for those inputs"""
from os import makedirs
from typing import (
    List,
    Dict,
)
from tqdm import tqdm
from multiprocessing import Pool
import networkx as nx
from pmotifs.GraphletOccurence import GraphletOccurrence
from pmotifs.PMotifGraph import PMotifGraph
from pmotifs.config import WORKERS
from pmotifs.pMetrics.PMetric import PMetric
from pmotifs.pMetrics.PMetricResult import PMetricResult


def process_graphlet_occurrences(
    g: nx.Graph, graphlet_occurrences: List[GraphletOccurrence], metrics: List[PMetric]
) -> List[PMetricResult]:
    """Calculate motif positional metrics"""

    result: Dict[str, Dict] = {m.name: {} for m in metrics}

    # Pre-Compute for metrics
    metric: PMetric
    for metric in tqdm(metrics, desc="Pre-computing metrics", leave=False):
        result[metric.name]["pre_compute"] = metric.pre_computation(g)

    # Calculate metrics
    with Pool(processes=WORKERS) as p:
        for metric in tqdm(metrics, desc="Calculating metrics", leave=False):
            result[metric.name]["graphlet_metrics"] = []
            args = [
                (g, g_oc.nodes, result[metric.name]["pre_compute"])
                for g_oc in graphlet_occurrences
            ]

            with tqdm(
                total=len(graphlet_occurrences),
                desc="Graphlet Occurrence Progress",
                leave=False,
            ) as pbar:
                for g_oc_result in p.starmap(
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
) -> List[PMetricResult]:
    """When pointed to a graph and a motif file, unzips the motif file, reads the graphs and calculates various
    positional metrics.
    Returns two lookups: Metric Name to Pre-Computation results, and Metric Name to raw metrics.
    raw metrics is in the same order as the graphlets."""
    g = nx.readwrite.edgelist.read_edgelist(
        pmotif_graph.get_graph_path(), data=False, create_using=nx.Graph
    )
    graphlet_occurrences: List[GraphletOccurrence] = pmotif_graph.load_graphlet_pos_zip(
        graphlet_size
    )

    metric_result_lookup = process_graphlet_occurrences(
        g, graphlet_occurrences, metrics
    )
    if save_to_disk:
        metric_output = pmotif_graph.get_pmetric_directory(graphlet_size)
        makedirs(metric_output)
        for metric_result in metric_result_lookup:
            metric_result.save_to_disk(metric_output)

    return metric_result_lookup
