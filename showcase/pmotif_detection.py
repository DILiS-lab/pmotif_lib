"""Perform a graphlet detection on the original and on generated random graphs,
calculates metrics on the resulting graphlets and compares them."""
from pathlib import Path
from typing import List

from scipy.stats import mannwhitneyu

from pmotifs.PMotifGraph import PMotifGraph, PMotifGraphWithRandomization
from pmotifs.config import DATASET_DIRECTORY
from pmotifs.graphlet_representation import graphlet_class_to_name
from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from pmotifs.pMetrics.PDegree import PDegree
from pmotifs.pMetrics.PMetric import PMetric
from pmotifs.positional_metrics import calculate_metrics


def main(edgelist: Path, output: Path, graphlet_size: int):
    degree_metric = PDegree()

    pmotif_graph = PMotifGraph(edgelist, output)
    original_metrics_by_graphlet_class = get_metrics_by_graphlet_classes(pmotif_graph, graphlet_size, [degree_metric])

    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(pmotif_graph, 10)
    del pmotif_graph

    random_metrics_by_class = []
    for random_graph in randomized_pmotif_graph.swapped_graphs:
        metrics_by_graphlet_class = get_metrics_by_graphlet_classes(random_graph, graphlet_size, [degree_metric])
        random_metrics_by_class.append(metrics_by_graphlet_class)

    # Analysis
    global_alpha = 0.05
    local_alpha = global_alpha / len(random_metrics_by_class)  # Bonferroni-Correction
    for graphlet_class in original_metrics_by_graphlet_class:
        for metric in original_metrics_by_graphlet_class[graphlet_class]:
            relevant_count = 0
            for random_metrics in random_metrics_by_class:
                mannwhitneyu_r = mannwhitneyu(
                    original_metrics_by_graphlet_class[graphlet_class][metric],
                    random_metrics[graphlet_class][metric],
                )
                if mannwhitneyu_r.pvalue > local_alpha:
                    # Degree Relevant!
                    relevant_count += 1
            print(f"{graphlet_class_to_name(graphlet_class)}: {relevant_count} out of {len(random_metrics_by_class)}"
                  f" random graphs show significant differences in their {metric} distribution!")


def get_metrics_by_graphlet_classes(pgraph: PMotifGraph, graphlet_size: int, metrics: List[PMetric]):
    run_gtrieScanner(
        graph_edgelist=pgraph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pgraph.get_graphlet_directory(),
    )

    graphlet_occurrences = pgraph.load_graphlet_pos_zip(graphlet_size)
    metric_results = calculate_metrics(pgraph, graphlet_size, metrics, True)

    by_graphlet_class = {}
    for i, g_oc in enumerate(graphlet_occurrences):
        if g_oc.graphlet_class not in by_graphlet_class:
            by_graphlet_class[g_oc.graphlet_class] = {}
        for metric_result in metric_results:
            by_graphlet_class[g_oc.graphlet_class][metric_result.metric_name] = metric_result.graphlet_metrics[i]

    return by_graphlet_class


if __name__ == "__main__":
    main(DATASET_DIRECTORY / "kaggle_star_wars.edgelist", Path("./showcase_output"), 3)
