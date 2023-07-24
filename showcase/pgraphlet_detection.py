"""Performs a `graphlet_size` graphlet detection and
calculates each metric in `metrics` for each graphlet occurrence."""
# Code in showcase intentionally duplicated, so examples can stand alone
# pylint: disable=duplicate-code
import shutil
from pathlib import Path

from pmotif_lib.p_motif_graph import PMotifGraph
from pmotif_lib.gtrieScanner.wrapper import run_gtrieScanner
from pmotif_lib.p_metric.p_degree import PDegree
from pmotif_lib.p_metric.metric_processing import calculate_metrics

DATASET = Path("./artifacts") / "karate_club.edgelist"
GRAPHLET_SIZE = 3
GTRIESCANNER_EXECUTABLE = "gtrieScanner"  # is in PATH
OUTPUT = Path("./artifacts") / "showcase_output"

WORKERS = 1


def main(edgelist: Path, output: Path, graphlet_size: int):
    """Run a p-graphlet detection (based on the positional metric 'degree')."""
    pmotif_graph = PMotifGraph(edgelist, output)

    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
    )

    degree_metric = PDegree()
    metric_results = calculate_metrics(
        pmotif_graph, graphlet_size, [degree_metric], True, workers=WORKERS,
    )

    graphlet_occurrences = pmotif_graph.load_graphlet_pos_zip(graphlet_size)
    print(graphlet_occurrences[0].graphlet_class, graphlet_occurrences[0].nodes)
    print(metric_results[0].graphlet_metrics[0])


if __name__ == "__main__":
    if OUTPUT.is_dir():
        shutil.rmtree(OUTPUT)
    main(DATASET, OUTPUT, GRAPHLET_SIZE)
