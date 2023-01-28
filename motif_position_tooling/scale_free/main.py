import json
from typing import List

from tqdm import tqdm
from uuid import uuid1

from motif_position_tooling.config import EXPERIMENT_OUT, GTRIESCANNER_EXECUTABLE
from motif_position_tooling.scale_free.generate_graphs import generate_graphs

from motif_position_tooling.utils.controller import gtrieScanner
from motif_position_tooling.utils.motif_io import MotifGraphWithRandomization, MotifGraph
from motif_position_tooling.utils.positional_metrics import calculate_metrics

BASENAME = f"scale_free_{uuid1()}"


# Step 1: Generate Scale Free Graphs and swap their edges
def generate_scale_free_graphs(
        num_of_graphs=100,
        num_of_random_graphs=100,
        num_of_nodes=100,
) -> List[MotifGraphWithRandomization]:
    return generate_graphs(
        num_of_graphs=num_of_graphs,
        num_of_random_graphs=num_of_random_graphs,
        number_of_nodes=num_of_nodes,
        experiment_dir=EXPERIMENT_OUT / BASENAME,
    )


def detect_motifs(motif_graphs: List[MotifGraphWithRandomization], motif_size: int):
    motif_graph: MotifGraphWithRandomization
    for motif_graph in tqdm(motif_graphs, desc="Motif Detection on Scale Free Graphs"):
        # Step 2.1: Detect Motifs for the scale free graph
        gtrieScanner(
            graph_edgelist=motif_graph.get_graph_path(),
            gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
            directed=False,
            motif_size=motif_size,
            output_directory=motif_graph.get_motif_directory(),
        )
        # Step 2.2: Detect Motifs for the corresponding edge-swapped graphs
        pbar_edge_swapped_graphs = tqdm(
            motif_graph.swapped_graphs,
            desc="\tMotif Detection on Edge Swapped Graphs",
            leave=False,
        )
        edge_swapped_graph: MotifGraph
        for edge_swapped_graph in pbar_edge_swapped_graphs:
            gtrieScanner(
                graph_edgelist=edge_swapped_graph.get_graph_path(),
                gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
                directed=False,
                motif_size=motif_size,
                output_directory=edge_swapped_graph.get_motif_directory(),
            )


# Step 3: Calculate Motif Positional Metrics
def calculate_metrics_on_graphs(motif_graphs: List[MotifGraphWithRandomization], motif_size: int):
    motif_graph: MotifGraphWithRandomization
    for motif_graph in tqdm(motif_graphs, desc="Motif Metrics on Scale Free Graphs"):

        data = calculate_metrics(motif_graph.get_graph_path(), motif_graph.get_motif_pos_zip(motif_size))
        with open(motif_graph.get_motif_metric_json(motif_size), "w") as f:
            json.dump(data, f)

        edge_swapped: MotifGraph
        for edge_swapped in tqdm(motif_graph.swapped_graphs, desc="Swappings", leave=False):
            data = calculate_metrics(edge_swapped.get_graph_path(), edge_swapped.get_motif_pos_zip(motif_size))
            with open(edge_swapped.get_motif_metric_json(motif_size), "w") as f:
                json.dump(data, f)


def main():
    graphs = generate_scale_free_graphs(5, 5, 100)

    pbar = tqdm([3, 4], desc="Processing Motif Size:")
    for k in pbar:
        pbar.set_description(f"Processing Motif Size: {k}")

        detect_motifs(graphs, k)
        calculate_metrics_on_graphs(graphs, k)


if __name__ == "__main__":
    main()
