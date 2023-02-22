import json
from typing import List

from tqdm import tqdm
from multiprocessing import Pool
from uuid import uuid1

from motif_position_tooling.config.config import WORKERS
from motif_position_tooling.config import EXPERIMENT_OUT, GTRIESCANNER_EXECUTABLE
from scale_free.generate_graphs import generate_graphs

from motif_position_tooling.gtrieScanner import run
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
        run(
            graph_edgelist=motif_graph.get_graph_path(),
            gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
            directed=False,
            motif_size=motif_size,
            output_directory=motif_graph.get_motif_directory(),
        )
        # Step 2.2: Detect Motifs for the corresponding edge-swapped graphs
        pbar_edge_swapped_graphs = tqdm(
            motif_graph.swapped_graphs,
            desc="Motif Detection on Edge Swapped Graphs",
            leave=False,
        )
        edge_swapped_graph: MotifGraph
        for edge_swapped_graph in pbar_edge_swapped_graphs:
            run(
                graph_edgelist=edge_swapped_graph.get_graph_path(),
                gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
                directed=False,
                motif_size=motif_size,
                output_directory=edge_swapped_graph.get_motif_directory(),
            )


def _calc_and_dump(args):
    """Calculates motif positional metrics and dumps them to disk"""
    graph: MotifGraph
    motif_size: int

    graph, motif_size = args
    data = calculate_metrics(graph, motif_size, disable_tqdm=True)
    with open(graph.get_motif_metric_json(motif_size), "w") as f:
        json.dump(data, f)


# Step 3: Calculate Motif Positional Metrics
def calculate_metrics_on_graphs(motif_graphs: List[MotifGraphWithRandomization], motif_size: int):
    pool = Pool(WORKERS)

    motif_graph: MotifGraphWithRandomization
    for motif_graph in tqdm(motif_graphs, desc="Motif Metrics on Scale Free Graphs"):
        _calc_and_dump((motif_graph, motif_size))

        for _ in tqdm(
            pool.imap_unordered(
                _calc_and_dump,
                zip(motif_graph.swapped_graphs, [motif_size] * len(motif_graph.swapped_graphs)),
                chunksize=5,
            ),
            desc="Swappings",
            leave=False,
            total=len(motif_graph.swapped_graphs),
        ):
            # Used to advance the progress bar
            pass


def main():
    graphs = generate_scale_free_graphs(5, 5, 100)

    pbar = tqdm([3, 4], desc="Processing Motif Size:")
    for k in pbar:
        pbar.set_description(f"Processing Motif Size: {k}")

        detect_motifs(graphs, k)
        calculate_metrics_on_graphs(graphs, k)


if __name__ == "__main__":
    main()
