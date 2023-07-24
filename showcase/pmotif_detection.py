"""Perform a graphlet detection on the original and on generated random graphs,
calculates metrics on the resulting graphlets and compares them."""
# Code in showcase intentionally duplicated, so examples can stand alone
# pylint: disable=duplicate-code
import shutil
from pathlib import Path
from typing import List

from scipy.stats import mannwhitneyu

from pmotif_lib.p_motif_graph import PMotifGraph, PMotifGraphWithRandomization
from pmotif_lib.graphlet_representation import graphlet_class_to_name
from pmotif_lib.gtrieScanner.wrapper import run_gtrieScanner
from pmotif_lib.p_metric.p_degree import PDegree
from pmotif_lib.p_metric.p_metric import PMetric
from pmotif_lib.p_metric.metric_processing import calculate_metrics


DATASET = Path("./artifacts") / "karate_club.edgelist"
GTRIESCANNER_EXECUTABLE = "gtrieScanner"  # is in PATH
GRAPHLET_SIZE = 3
OUTPUT = Path("./artifacts") / "showcase_output"
NUMBER_OF_RANDOM_GRAPHS = 10

WORKERS = 1


def main(
    edgelist: Path, output: Path, graphlet_size: int, number_of_random_graphs: int
):
    """Run a p-motif detection (based on the positional metric 'degree') and basic analysis."""
    degree_metric = PDegree()

    pmotif_graph = PMotifGraph(edgelist, output)
    original_metrics_by_graphlet_class = get_metrics_by_graphlet_classes(
        pmotif_graph, graphlet_size, [degree_metric]
    )

    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(
        pmotif_graph, number_of_random_graphs
    )
    del pmotif_graph

    random_metrics_by_class = []
    for random_graph in randomized_pmotif_graph.swapped_graphs:
        metrics_by_graphlet_class = get_metrics_by_graphlet_classes(
            random_graph, graphlet_size, [degree_metric]
        )
        random_metrics_by_class.append(metrics_by_graphlet_class)

    analyse(original_metrics_by_graphlet_class, random_metrics_by_class)


def analyse(original_metrics_by_graphlet_class, random_metrics_by_class):
    """Perform pair-wise mann whitney u test between the original graph and the random graphs.
    Print how many random graphs are determined as significant, grouped by graphlet class and
    positional metric."""
    global_alpha = 0.05
    local_alpha = global_alpha / len(random_metrics_by_class)  # Bonferroni-Correction
    for graphlet_class, metric_lookup in original_metrics_by_graphlet_class.items():
        for metric_name, metric_values in metric_lookup.items():
            relevant_count = 0
            for random_metrics in random_metrics_by_class:
                mannwhitneyu_r = mannwhitneyu(
                    metric_values,
                    random_metrics[graphlet_class][metric_name],
                )
                if mannwhitneyu_r.pvalue > local_alpha:
                    # Degree Relevant!
                    relevant_count += 1
            print(
                f"{graphlet_class_to_name(graphlet_class)}:"
                f" {relevant_count} out of {len(random_metrics_by_class)}"
                f" random graphs show significant differences in their {metric_name} distribution!"
            )


def get_metrics_by_graphlet_classes(
    pgraph: PMotifGraph, graphlet_size: int, metrics: List[PMetric]
):
    """Perform a graphlet detection, calculate given metrics on detected graphlets, and
    return the metrics as a lookup from graphlet class and metric name to the metric values."""
    run_gtrieScanner(
        graph_edgelist=pgraph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pgraph.get_graphlet_directory(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
    )

    graphlet_occurrences = pgraph.load_graphlet_pos_zip(graphlet_size)
    metric_results = calculate_metrics(pgraph, graphlet_size, metrics, True, workers=WORKERS)

    by_graphlet_class = {}
    for i, g_oc in enumerate(graphlet_occurrences):
        if g_oc.graphlet_class not in by_graphlet_class:
            by_graphlet_class[g_oc.graphlet_class] = {}
        for metric_result in metric_results:
            by_graphlet_class[g_oc.graphlet_class][
                metric_result.metric_name
            ] = metric_result.graphlet_metrics[i]

    return by_graphlet_class


if __name__ == "__main__":
    if OUTPUT.is_dir():
        shutil.rmtree(OUTPUT)
    main(DATASET, OUTPUT, GRAPHLET_SIZE, NUMBER_OF_RANDOM_GRAPHS)
