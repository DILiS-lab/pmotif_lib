import zipfile

import networkx as nx
from pathlib import Path
from typing import List
from os import listdir


def write_shifted_edgelist(g: nx.Graph, path: Path, shift=1, reindex=False):
    node_mapping = dict(zip(g.nodes, g.nodes))
    if reindex:
        # Create node mapping
        node_mapping = {n: i for i, n in enumerate(g.nodes)}

    lines = [f"{node_mapping[u] + shift} {node_mapping[v] + shift}\n" for u, v in g.edges()]
    with open(path, "w") as out:
        out.writelines(lines)


def load_motif_zip(motif_zip: Path) -> List[List[str]]:
    with zipfile.ZipFile(motif_zip, 'r') as zfile:
        motifs = []
        for line in zfile.open("motif_pos"):
            label, *nodes = line.decode().split(" ")
            motifs.append([n.strip() for n in nodes])
    return motifs


class MotifGraph:
    """An Object wrapper around the folder structure of a graph which is subject to motif detection
    Such a graph's filesystem equavalent looks like this
    -some_path
    --<graphname>.edgelist
    --<graphname>.edgelist_motifs/
    ----<motif_size>/
    ------motif_freq
    ------motif_pos.zip
    --edge_swappings/
    ----0_random.edgelist
    ----1_random.edgelist
    ----<n>_random.edgelist
    ----1_random.edgelist_motifs/
    ------<motif_size>/
    --------motif_freq
    --------motif_pos.zip
    ----2_random.edgelist_motifs/
    ------<motif_size>/
    --------motif_freq
    --------motif_pos.zip
    ----<n>_random.edgelist_motifs/
    ------<motif_size>/
    --------motif_freq
    --------motif_pos.zip
    """
    def __init__(self, directory: Path, graph_name: str):
        self.directory = directory
        self.graph_name = graph_name

    def get_graph_path(self) -> Path:
        return self.directory / self.graph_name

    def get_motif_directory(self) -> Path:
        return self.directory / (self.graph_name + "_motifs")

    def get_motif_output_directory(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size)

    def get_motif_freq_file(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size) / "motif_freq"

    def get_motif_pos_zip(self, motif_size: int) -> Path:
        return self.get_motif_directory() / str(motif_size) / "motif_pos.zip"


class MotifGraphWithRandomization(MotifGraph):
    EDGE_SWAPPED_GRAPH_DIRECTORY_NAME = "edge_swappings"

    def __init__(self, directory: Path, graph_name: str):
        super().__init__(directory, graph_name)

        self.edge_swapped_graph_directory = self.directory / self.EDGE_SWAPPED_GRAPH_DIRECTORY_NAME

        swapped_edge_lists = [
            f
            for f in listdir(self.edge_swapped_graph_directory)
            if (self.edge_swapped_graph_directory / f).is_file()
        ]
        self.swapped_graphs: List[MotifGraph] = [
            MotifGraph(self.edge_swapped_graph_directory, f)
            for f in swapped_edge_lists
        ]
