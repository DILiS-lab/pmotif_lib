"""Calculates and returns all induced subgraphs of size `graphlet_size`,
grouped by their isomorphic class (returns all graphlet occurrences)"""
# Code in showcase intentionally duplicated, so examples can stand alone
# pylint: disable=duplicate-code
import shutil
from pathlib import Path

from pmotif_lib.p_motif_graph import PMotifGraph
from pmotif_lib.config import DATASET_DIRECTORY, EXPERIMENT_OUT
from pmotif_lib.gtrieScanner.wrapper import run_gtrieScanner


DATASET = DATASET_DIRECTORY / "karate_club.edgelist"
GRAPHLET_SIZE = 3
OUTPUT = EXPERIMENT_OUT / "showcase_output"


def main(edgelist: Path, output: Path, graphlet_size: int):
    """Run a graphlet detection."""
    pmotif_graph = PMotifGraph(edgelist, output)

    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )

    graphlet_occurrences = pmotif_graph.load_graphlet_pos_zip(graphlet_size)
    print(graphlet_occurrences[0].graphlet_class, graphlet_occurrences[0].nodes)


if __name__ == "__main__":
    if OUTPUT.is_dir():
        shutil.rmtree(OUTPUT)
    main(DATASET, OUTPUT, GRAPHLET_SIZE)
