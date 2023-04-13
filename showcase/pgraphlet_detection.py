"""Performs a `graphlet_size` graphlet detection and
calculates each metric in `metrics` for each graphlet occurrence."""
from pathlib import Path

from pmotifs.PMotifGraph import PMotifGraph
from pmotifs.config import DATASET_DIRECTORY
from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from pmotifs.pMetrics.PDegree import PDegree
from pmotifs.positional_metrics import calculate_metrics


def main(edgelist: Path, output: Path, graphlet_size: int):
    pmotif_graph = PMotifGraph(edgelist, output)

    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )

    degree_metric = PDegree()
    metric_results = calculate_metrics(pmotif_graph, graphlet_size, [degree_metric], True)

    graphlet_occurrences = pmotif_graph.load_graphlet_pos_zip(graphlet_size)
    print(graphlet_occurrences[0].graphlet_class, graphlet_occurrences[0].nodes)
    print(metric_results[0].graphlet_metrics[0])


if __name__ == "__main__":
    main(DATASET_DIRECTORY / "kaggle_star_wars.edgelist", Path("./showcase_output"), 3)
