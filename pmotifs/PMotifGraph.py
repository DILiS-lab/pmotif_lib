import pickle
import zipfile
from pathlib import Path
from os import listdir
from typing import List, Dict
from math import sqrt
import networkx as nx

import pmotifs.gtrieScanner.graph_io as graph_io
import pmotifs.gtrieScanner.parsing as parsing
from pmotifs.GraphletOccurence import GraphletOccurrence


class PMotifGraph:
    """An Object wrapper around the folder structure of a graph which is subject to pmotif detection"""
    def __init__(self, edgelist_path: Path, output_directory: Path):
        self.edgelist_path = edgelist_path
        self.output_directory = output_directory

    def get_graph_path(self) -> Path:
        return self.edgelist_path

    def load_graph(self) -> nx.Graph:
        return graph_io.read_edgelist(self.get_graph_path())

    def get_graphlet_directory(self) -> Path:
        return self.output_directory / (self.edgelist_path.name + "_motifs")

    def get_graphlet_output_directory(self, graphlet_size: int) -> Path:
        return self.get_graphlet_directory() / str(graphlet_size)

    def get_graphlet_freq_file(self, graphlet_size: int) -> Path:
        return self.get_graphlet_directory() / str(graphlet_size) / "motif_freq"

    def load_graphlet_freq_file(self, graphlet_size: int) -> Dict[str, int]:
        """Return a lookup from graphlet-class to count of graphlet-occurrence"""
        return parsing.parse_graphlet_detection_results_table(self.get_graphlet_freq_file(graphlet_size), graphlet_size)

    def get_graphlet_pos_zip(self, graphlet_size: int) -> Path:
        return self.get_graphlet_directory() / str(graphlet_size) / "motif_pos.zip"

    def load_graphlet_pos_zip(self, graphlet_size: int) -> List[GraphletOccurrence]:
        """Returns all motifs in a lookup from their index to their id (adj matrix string) and a list of their nodes"""
        with zipfile.ZipFile(self.get_graphlet_pos_zip(graphlet_size), 'r') as zfile:
            graphlets = []
            graphlet_size = None
            for i, line in enumerate(zfile.open("motif_pos")):
                # Each line looks like this
                # '<adj.matrix written in one line>: <node1> <node2> ...'
                label, *nodes = line.decode().split(" ")
                label = label[:-1]  # Strip the trailing ':'

                # For reasons unknown, gtrieScanner reverses the adj matrix when saving occurrences
                label = label[::-1]

                if graphlet_size is None:
                    graphlet_size = int(sqrt(len(label)))

                graphlet_class = " ".join([
                    label[i:i + graphlet_size]
                    for i in range(0, graphlet_size * graphlet_size, graphlet_size)
                ])
                graphlets.append(GraphletOccurrence(graphlet_class=graphlet_class, nodes=[n.strip() for n in nodes]))
        return graphlets

    def get_graphlet_metric_file(self, graphlet_size: int) -> Path:
        return self.get_graphlet_directory() / str(graphlet_size) / "motif_metric_data.pickle"

    def load_graphlet_metric_file(self, graphlet_size: int) -> Dict:
        with open(self.get_graphlet_metric_file(graphlet_size), "rb") as f:
            graphlet_metrics = pickle.load(f)
        return graphlet_metrics


class PMotifGraphWithRandomization(PMotifGraph):
    """A PMotifGraph g which contains references to other p motif graphs that were generated from g using a null model"""
    EDGE_SWAPPED_GRAPH_DIRECTORY_NAME = "edge_swappings"

    def __init__(self, edgelist_path: Path, output_directory: Path):
        super().__init__(edgelist_path, output_directory)

        self.edge_swapped_graph_directory = self.output_directory / self.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME

        swapped_edge_lists = [
            f
            for f in listdir(self.edge_swapped_graph_directory)
            if (self.edge_swapped_graph_directory / str(f)).is_file()
        ]
        self.swapped_graphs: List[PMotifGraph] = [
            PMotifGraph(self.edge_swapped_graph_directory / str(f), self.edge_swapped_graph_directory)
            for f in swapped_edge_lists
        ]
