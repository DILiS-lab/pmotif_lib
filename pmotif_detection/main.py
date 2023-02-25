import json
from pathlib import Path
from os import makedirs
import networkx as nx

from pmotifs.PMotifGraph import PMotifGraph
from pmotifs.config import GTRIESCANNER_EXECUTABLE
from pmotifs.gtrieScanner.wrapper import run_gtrieScanner
from pmotifs.positional_metrics import calculate_metrics


def load_graph(graph_edgelist, output_directory):
    nx_graph = nx.read_edgelist(
        graph_edgelist,
        create_using=nx.Graph,  # Asserts undirected graph
        data=False,  # Asserts unweighted graph
    )

    if len(list(nx.selfloop_edges(nx_graph))) > 0:
        raise ValueError("Graph contains Self-Loops!")  # Asserts simple graph

    if min(map(int, nx_graph.nodes)) < 1:
        raise ValueError("Graph contains node ids below '1'!")  # Assert lowest node index is >= 1

    return PMotifGraph(graph_edgelist, output_directory)


def main(edgelist, out, graphlet_size):
    print("Loading Graph")
    pmotif_graph = load_graph(edgelist, out)
    print("Graphlet Detection")
    run_gtrieScanner(
        graph_edgelist=pmotif_graph.get_graph_path(),
        gtrieScanner_executable=GTRIESCANNER_EXECUTABLE,
        directed=False,
        graphlet_size=graphlet_size,
        output_directory=pmotif_graph.get_graphlet_directory(),
    )
    print("Calculating positional metrics")
    positional_metrics = calculate_metrics(pmotif_graph, graphlet_size)
    print("Dumping positional metrics")
    positional_metrics.save(pmotif_graph.get_positional_data_directory(graphlet_size))


if __name__ == "__main__":
    GRAPH_EDGELIST = Path("/home/timgarrels/masterthesis/datasets/yeastInter_st.txt")
    OUT = Path("/home/timgarrels/masterthesis/output/pmotif_detection")
    makedirs(OUT, exist_ok=True)

    GRAPHLET_SIZE = 3

    main(GRAPH_EDGELIST, OUT, GRAPHLET_SIZE)
