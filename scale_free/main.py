import pickle
from typing import List

from tqdm import tqdm
from multiprocessing import Pool
from uuid import uuid1

from pmotifs.config.config import WORKERS
from pmotifs.config import EXPERIMENT_OUT, GTRIESCANNER_EXECUTABLE
from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from scale_free.generate_graphs import generate_graphs

from pmotifs.utils.motif_io import PMotifGraphWithRandomization, PMotifGraph
from pmotifs.utils.positional_metrics import calculate_metrics

BASENAME = f"scale_free_{uuid1()}"


# Step 1: Generate Scale Free Graphs and swap their edges
def generate_scale_free_graphs(
        num_of_graphs=100,
        num_of_random_graphs=100,
        num_of_nodes=100,
) -> List[PMotifGraphWithRandomization]:
    return generate_graphs(
        num_of_graphs=num_of_graphs,
        num_of_random_graphs=num_of_random_graphs,
        number_of_nodes=num_of_nodes,
        experiment_dir=EXPERIMENT_OUT / BASENAME,
    )


def detect_motifs(motif_graphs: List[PMotifGraphWithRandomization], motif_size: int):
    motif_graph: PMotifGraphWithRandomization
    for motif_graph in tqdm(motif_graphs, desc="Motif Detection on Scale Free Graphs"):
        # Step 2.1: Detect Motifs for the scale free graph
        run_gtrieScanner(
            graph_edgelist=motif_graph.get_graph_path(),
            gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
            directed=False,
            graphlet_size=motif_size,
            output_directory=motif_graph.get_graphlet_directory(),
        )
        # Step 2.2: Detect Motifs for the corresponding edge-swapped graphs
        pbar_edge_swapped_graphs = tqdm(
            motif_graph.swapped_graphs,
            desc="Motif Detection on Edge Swapped Graphs",
            leave=False,
        )
        edge_swapped_graph: PMotifGraph
        for edge_swapped_graph in pbar_edge_swapped_graphs:
            run_gtrieScanner(
                graph_edgelist=edge_swapped_graph.get_graph_path(),
                gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
                directed=False,
                graphlet_size=motif_size,
                output_directory=edge_swapped_graph.get_graphlet_directory(),
            )


def _calc_and_dump(args):
    """Calculates motif positional metrics and dumps them to disk"""
    graph: PMotifGraph
    motif_size: int

    graph, motif_size = args
    data = calculate_metrics(graph, motif_size)
    with open(graph.get_graphlet_metric_file(motif_size), "wb") as f:
        pickle.dump(data, f)


# Step 3: Calculate Motif Positional Metrics
def calculate_metrics_on_graphs(motif_graphs: List[PMotifGraphWithRandomization], motif_size: int):
    pool = Pool(WORKERS)

    motif_graph: PMotifGraphWithRandomization
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
    graphs = generate_scale_free_graphs(20, 10, 20)

    pbar = tqdm([3, 4], desc="Processing Motif Size:")
    for k in pbar:
        pbar.set_description(f"Processing Motif Size: {k}")

        detect_motifs(graphs, k)
        calculate_metrics_on_graphs(graphs, k)


if __name__ == "__main__":
    main()
