"""Contains classes to manage disk locations of p-motif detection input, intermediate results,
and output."""
import zipfile
from math import sqrt
from os import listdir, makedirs
from pathlib import Path
from typing import List, Dict

import networkx as nx
from tqdm import tqdm

from pmotif_lib.gtrieScanner import graph_io
from pmotif_lib.gtrieScanner import parsing
from pmotif_lib.graphlet_occurence import GraphletOccurrence

from pmotif_lib.randomization import swap_edges_markov_chain


class PMotifGraph:
    """An Object wrapper around the folder structure
    of a graph which is subject to pmotif detection"""

    def __init__(self, edgelist_path: Path, output_directory: Path):
        self.edgelist_path = edgelist_path
        self.output_directory = output_directory

    def get_graph_path(self) -> Path:
        """Return the edgelist of the represented graph."""
        return self.edgelist_path

    def load_graph(self) -> nx.Graph:
        """Load the represented graph as nx.Graph object."""
        return graph_io.read_edgelist(self.get_graph_path())

    def get_graphlet_directory(self) -> Path:
        """Return directory where all detected graphlets are stored."""
        return self.output_directory / (self.edgelist_path.name + "_motifs")

    def get_graphlet_output_directory(self, graphlet_size: int) -> Path:
        """Return the output directory for all graphlets of given size."""
        return self.get_graphlet_directory() / str(graphlet_size)

    def get_graphlet_freq_file(self, graphlet_size: int) -> Path:
        """Return the location of the gTrieScanner output file listing meta-information
        as well as all occurring graphlet classes and their frequencies."""
        return self.get_graphlet_directory() / str(graphlet_size) / "motif_freq"

    def load_graphlet_freq_file(self, graphlet_size: int) -> Dict[str, int]:
        """Return a lookup from graphlet-class to count of graphlet-occurrence"""
        return parsing.parse_graphlet_detection_results_table(
            self.get_graphlet_freq_file(graphlet_size), graphlet_size
        )

    def get_graphlet_pos_zip(self, graphlet_size: int) -> Path:
        """Return the location of the compressed output-file of gTrieScanner,
        containing all graphlet occurrences of all classes."""
        return self.get_graphlet_directory() / str(graphlet_size) / "motif_pos.zip"

    def load_graphlet_pos_zip(
        self, graphlet_size: int, supress_tqdm: bool = False
    ) -> List[GraphletOccurrence]:
        """Returns all motifs in a lookup
        from their index to their id (adj matrix string) and a list of their nodes"""
        graphlet_count = sum(self.load_graphlet_freq_file(graphlet_size).values())

        with zipfile.ZipFile(self.get_graphlet_pos_zip(graphlet_size), "r") as zfile:
            graphlets = []
            graphlet_size = None
            with zfile.open("motif_pos") as motif_pos_file:
                for i, line in tqdm(
                    enumerate(motif_pos_file),
                    desc="Load Graphlet Positions",
                    total=graphlet_count,
                    leave=False,
                    disable=supress_tqdm,
                ):
                    # Each line looks like this
                    # '<adj.matrix written in one line>: <node1> <node2> ...'
                    label, *nodes = line.decode().split(" ")
                    label = label[:-1]  # Strip the trailing ':'

                    # gtrieScanner reverses the adj matrix when saving occurrences
                    label = label[::-1]

                    if graphlet_size is None:
                        graphlet_size = int(sqrt(len(label)))

                    graphlet_class = " ".join(
                        [
                            label[i : i + graphlet_size]
                            for i in range(
                                0, graphlet_size * graphlet_size, graphlet_size
                            )
                        ]
                    )
                    graphlets.append(
                        GraphletOccurrence(
                            graphlet_class=graphlet_class,
                            nodes=[n.strip() for n in nodes],
                        )
                    )
            return graphlets

    def get_pmetric_directory(self, graphlet_size: int) -> Path:
        """Return the directory to store p-metrics calculated on graphlets of the given size."""
        return self.get_graphlet_directory() / str(graphlet_size) / "pmetrics"


class PMotifGraphWithRandomization(PMotifGraph):
    """A PMotifGraph g which contains references to other p motif graphs
    that were generated from g using a null model"""

    EDGE_SWAPPED_GRAPH_DIRECTORY_NAME = "edge_swappings"

    def __init__(self, edgelist_path: Path, output_directory: Path):
        super().__init__(edgelist_path, output_directory)

        self.edge_swapped_graph_directory = (
            self.output_directory / self.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME
        )

        swapped_edge_lists = [
            f
            for f in listdir(self.edge_swapped_graph_directory)
            if (self.edge_swapped_graph_directory / str(f)).is_file()
        ]
        self.swapped_graphs: List[PMotifGraph] = [
            PMotifGraph(
                self.edge_swapped_graph_directory / str(f),
                self.edge_swapped_graph_directory,
            )
            for f in swapped_edge_lists
        ]

    @staticmethod
    def create_random_graph(graph: nx.Graph) -> nx.Graph:
        """Method used to create random graphs. Overwrite to set your own random graph method"""
        swaps_per_edge = 3
        tries_per_swap = 10
        return swap_edges_markov_chain(graph, swaps_per_edge, tries_per_swap)

    @staticmethod
    def create_from_pmotif_graph(
        pmotif_graph: PMotifGraph,
        num_random_graphs: int,
    ):
        """num_random_graphs determines how many random graphs are generated
        if num_random_graphs is >= 0 the call fails if random graphs are already present,
        otherwise, they are generated
        if num_random_graphs is -1, no additional graphs are generated,
        however, the already present random graphs will be used
        """
        graph = pmotif_graph.load_graph()
        if num_random_graphs <= -1:
            # Do not generate additional graphs
            return PMotifGraphWithRandomization(
                pmotif_graph.edgelist_path,
                pmotif_graph.output_directory,
            )

        edge_swapped_dir = (
            pmotif_graph.output_directory
            / PMotifGraphWithRandomization.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME
        )
        makedirs(edge_swapped_dir, exist_ok=True)

        swapped_edge_lists = [
            str(f)
            for f in listdir(edge_swapped_dir)
            if (edge_swapped_dir / str(f)).is_file()
        ]

        if len(swapped_edge_lists) > 0 and num_random_graphs >= 0:
            raise ValueError(
                "`num_random_graphs` >= 0, but random graphs already present, abort. "
                "Did you mean `-1`?"
            )

        required_shift = 0
        min_node = None
        for node in graph.nodes:
            if min_node is None:
                min_node = int(node)
            if int(node) < min_node:
                min_node = int(node)

        if min_node < 1:
            required_shift = abs(min_node) + 1

        for i in tqdm(
            range(num_random_graphs), desc="Creating Random Graphs", leave=False
        ):
            random_g = PMotifGraphWithRandomization.create_random_graph(graph.copy())

            graph_io.write_shifted_edgelist(
                random_g,
                edge_swapped_dir / f"{i}_random.edgelist",
                shift=required_shift,
            )

        return PMotifGraphWithRandomization(
            pmotif_graph.edgelist_path,
            pmotif_graph.output_directory,
        )
