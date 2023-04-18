"""Perform a graphlet detection on the original and on generated random graphs"""
import shutil
from pathlib import Path
from statistics import mean, stdev

from pmotif_lib.p_motif_graph import PMotifGraph, PMotifGraphWithRandomization
from pmotif_lib.config import DATASET_DIRECTORY
from pmotif_lib.graphlet_representation import graphlet_class_to_name
from pmotif_lib.gtrieScanner.wrapper import run_gtrieScanner


DATASET = DATASET_DIRECTORY / "kaggle_star_wars.edgelist"
GRAPHLET_SIZE = 3
NUMBER_OF_RANDOM_GRAPHS = 10
OUTPUT = Path("./showcase_output")


def main(
    edgelist: Path, output: Path, graphlet_size: int, number_of_random_graphs: int
):
    pmotif_graph = PMotifGraph(edgelist, output)

    original_frequency = graphlet_detection(pmotif_graph, graphlet_size)

    randomized_pmotif_graph = PMotifGraphWithRandomization.create_from_pmotif_graph(
        pmotif_graph, number_of_random_graphs
    )

    random_frequencies = []
    for random_graph in randomized_pmotif_graph.swapped_graphs:
        random_frequency = graphlet_detection(random_graph, graphlet_size)
        random_frequencies.append(random_frequency)

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
    run_gtrieScanner(
        graph_edgelist=pgraph.get_graph_path(),
        graphlet_size=graphlet_size,
        output_directory=pgraph.get_graphlet_directory(),
    )

    graphlet_occurrences = pgraph.load_graphlet_pos_zip(graphlet_size)
    return graphlet_occurrences_to_class_frequencies(graphlet_occurrences)


def graphlet_occurrences_to_class_frequencies(graphlet_occurrences):
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
