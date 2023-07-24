"""Perform a graphlet detection on the original and on generated random graphs"""
# Code in showcase intentionally duplicated, so examples can stand alone
# pylint: disable=duplicate-code
import shutil
from pathlib import Path
from statistics import mean, stdev

from pmotif_lib.p_motif_graph import PMotifGraph, PMotifGraphWithRandomization
from pmotif_lib.graphlet_representation import graphlet_class_to_name
from pmotif_lib.gtrieScanner.wrapper import run_gtrieScanner


DATASET = Path("./artifacts") / "karate_club.edgelist"
GRAPHLET_SIZE = 3
GTRIESCANNER_EXECUTABLE = "gtrieScanner"  # is in PATH
OUTPUT = Path("./artifacts") / "showcase_output"
NUMBER_OF_RANDOM_GRAPHS = 10


def main(
    edgelist: Path, output: Path, graphlet_size: int, number_of_random_graphs: int
):
    """Run a motif detection."""
    pmotif_graph = PMotifGraph(edgelist, output)

    original_frequency = graphlet_detection(pmotif_graph, graphlet_size)

    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(
        pmotif_graph, number_of_random_graphs
    )

    random_frequencies = []
    for random_graph in randomized_pmotif_graph.swapped_graphs:
        random_frequency = graphlet_detection(random_graph, graphlet_size)
        random_frequencies.append(random_frequency)

    analyse(original_frequency, random_frequencies)


def analyse(original_frequency, random_frequencies):
    """For each graphlet class, print its occurrence frequency and use the z-score
    to compare the frequencies of each graphlet class."""
    print({graphlet_class_to_name(k): v for k, v in original_frequency.items()})
    for graphlet_class, frequency in original_frequency.items():
        all_random_frequencies = [
            r_f.get(graphlet_class, 0) for r_f in random_frequencies
        ]
        z_score = (frequency - mean(all_random_frequencies)) / stdev(
            all_random_frequencies
        )
        print(
            f"z-Score for {graphlet_class_to_name(graphlet_class)}: {round(z_score, 2)}"
        )


def graphlet_detection(pgraph: PMotifGraph, graphlet_size: int):
    """Perform a graphlet detection and return the graphlet class frequencies."""
    run_gtrieScanner(
        graph_edgelist=pgraph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pgraph.get_graphlet_directory(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
    )

    graphlet_occurrences = pgraph.load_graphlet_pos_zip(graphlet_size)
    return graphlet_occurrences_to_class_frequencies(graphlet_occurrences)


def graphlet_occurrences_to_class_frequencies(graphlet_occurrences):
    """Return a lookup from graphlet class to graphlet class frequency."""
    freq = {}
    for graphlet_occurrence in graphlet_occurrences:
        if graphlet_occurrence.graphlet_class not in freq:
            freq[graphlet_occurrence.graphlet_class] = 0
        freq[graphlet_occurrence.graphlet_class] += 1
    return freq


if __name__ == "__main__":
    if OUTPUT.is_dir():
        shutil.rmtree(OUTPUT)
    main(DATASET, OUTPUT, GRAPHLET_SIZE, NUMBER_OF_RANDOM_GRAPHS)
