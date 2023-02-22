import pickle
import zipfile
from pathlib import Path
from os import listdir
from typing import List, Dict
from math import sqrt
import networkx as nx

import motif_position_tooling.gtrieScanner.graph_io as graph_io
import motif_position_tooling.gtrieScanner.parsing as parsing
from motif_position_tooling.utils.GraphletOccurence import GraphletOccurrence


class MotifGraph:
    """An Object wrapper around the folder structure of a graph which is subject to motif detection"""
    def __init__(self, directory: Path, graph_name: str, output_directory: Path = None):
        self.directory = directory
        self.output_directory = self.directory if output_directory is None else output_directory
        self.graph_name = graph_name

    def get_graph_path(self) -> Path:
        return self.directory / self.graph_name

    def load_graph(self) -> nx.Graph:
        return graph_io.read_edgelist(self.get_graph_path())

    def get_motif_directory(self) -> Path:
        return self.output_directory / (self.graph_name + "_motifs")

    def get_motif_output_directory(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size)

    def get_motif_freq_file(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size) / "motif_freq"

    def load_motif_freq_file(self, motif_size: int) -> Dict[str, int]:
        """Return a lookup from motif-id to count of motif occurrence"""
        return parsing.parse_motif_analysis_results_table(self.get_motif_freq_file(motif_size))

    def get_motif_pos_zip(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size) / "motif_pos.zip"

    def load_motif_pos_zip(self, motif_size: int) -> List[GraphletOccurrence]:
        """Returns all motifs in a lookup from their index to their id (adj matrix string) and a list of their nodes"""
        with zipfile.ZipFile(self.get_motif_pos_zip(motif_size), 'r') as zfile:
            motifs = []
            motif_size = None
            for i, line in enumerate(zfile.open("motif_pos")):
                # Each line looks like this
                # '<adj.matrix written in one line>: <node1> <node2> ...'
                label, *nodes = line.decode().split(" ")
                label = label[:-1]  # Strip the trailing ':'
                if motif_size is None:
                    motif_size = int(sqrt(len(label)))

                motif_id = " ".join([label[i:i+motif_size] for i in range(0, motif_size * motif_size, motif_size)])
                motifs.append(GraphletOccurrence(graphlet_class=motif_id, nodes=[n.strip() for n in nodes]))
        return motifs

    def get_motif_metric_file(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size) / "motif_metric_data.pickle"

    def load_motif_metric_file(self, motif_size: int) -> Dict:
        with open(self.get_motif_metric_file(motif_size), "rb") as f:
            motif_metrics = pickle.load(f)
        return motif_metrics


class MotifGraphWithRandomization(MotifGraph):
    """A MotifGraph g which contains references to other motif graphs that were generated from g using a null model"""
    EDGE_SWAPPED_GRAPH_DIRECTORY_NAME = "edge_swappings"

    def __init__(self, directory: Path, graph_name: str):
        super().__init__(directory, graph_name)

        self.edge_swapped_graph_directory = self.directory / self.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME

        swapped_edge_lists = [
            f
            for f in listdir(self.edge_swapped_graph_directory)
            if (self.edge_swapped_graph_directory / str(f)).is_file()
        ]
        self.swapped_graphs: List[MotifGraph] = [
            MotifGraph(self.edge_swapped_graph_directory, str(f))
            for f in swapped_edge_lists
        ]
