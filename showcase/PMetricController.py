from pathlib import Path
from typing import Union, List, Dict, Callable, Tuple

import networkx as nx

from showcase.PMetric import PMetric
from pmotifs.randomization import swap_edges_markov_chain


GraphletOccurrence = List[str]
GraphletClass = str
NamedPMetricLookup = Dict[str, float]

GraphletDetectionResult = Dict[GraphletClass, List[GraphletOccurrence]]
PGraphletDetectionResult = Dict[
    GraphletClass,
    Dict[GraphletOccurrence, NamedPMetricLookup]
]


class PMetricController:
    """Object offering pmotif pipeline interface and disk managing capabilities"""

    def __init__(self, graph: nx.Graph, graph_name: str, output: Union[Path, None] = None):
        """Create a new PMetricController
        output: If None, all computation will stay in RAM.
                 If a Path object, computations will be loaded and stored there
        """
        self._graph = graph
        self._graph_name = graph_name
        self._output = output

        self._create_directory_structure()
        self._assure_result_integrity()
        self._load_stored_results()

    """----- Disk Interaction -----"""

    def _create_directory_structure(self):
        """Creates the basic directory structure for output, does not overwrite"""
        raise NotImplemented()

    def _assure_result_integrity(self):
        """Walks over results on disk and removes all unfinished results."""
        raise NotImplemented()

    def _load_stored_results(self):
        """Load results present on disk."""
        raise NotImplemented()

    """----- Interfaces -----"""

    def graphlet_detection(self, graphlet_size: int) -> GraphletDetectionResult:
        """Calculates and returns all induced subgraphs of size `graphlet_size`,
        grouped by their isomorphic class (returns all graphlet occurrences)"""
        raise NotImplemented()

    def p_graphlet_detection(self, graphlet_size: int, metrics: List[PMetric]) -> PGraphletDetectionResult:
        """Performs a `graphlet_size` graphlet detection and
        calculates each metric in `metrics` for each graphlet occurrence."""
        raise NotImplemented()

    def motif_detection(
        self,
        random_graphs: int = 1000,
        method: Callable[[nx.Graph], nx.Graph] = lambda g: swap_edges_markov_chain(g, 3, 10),
    ) -> Tuple[GraphletDetectionResult, List[GraphletDetectionResult]]:
        """Perform a graphlet detection and generated random graphs.

        Creates `random_graphs` many graphs using `method`
        Per defaults generates 1000 random graphs by using a markov chain edge swap model,
        where each edge is swapped 3 times, with 10 tries to find a valid swap per swap.

        Returns the graphlets of the original graph and a list of graphlets for each random graph.
        Graphlets are a lookup from graphlet class to a list of induced subgraphs.
        """
        raise NotImplemented()

    def p_motif_detection(
        self,
        metrics: List[PMetric],
        random_graphs: int = 1000,
        method: Callable[[nx.Graph], nx.Graph] = lambda g: swap_edges_markov_chain(g, 3, 10),
    ) -> Tuple[PGraphletDetectionResult, List[PGraphletDetectionResult]]:
        """Performs a `graphlet_size` graphlet detection and generated random graphs, and
        calculates each metric in `metrics` for each graphlet occurrence.

        Creates `random_graphs` many graphs using `method`
        Per defaults generates 1000 random graphs by using a markov chain edge swap model,
        where each edge is swapped 3 times, with 10 tries to find a valid swap per swap.

        Returns the p-graphlets of the original graph and a list of p-graphlets for each random graph, and all their
        respective metrics.
        """
        raise NotImplemented()

    """----- Disk Interaction -----"""

    def wipe(self):
        raise NotImplemented()

    def clear_all(self):
        raise NotImplemented()

    def clear_graphlets(self):
        raise NotImplemented()

    def clear_metrics(self):
        raise NotImplemented()

    def clear_random_graphs(self):
        raise NotImplemented()

    def clear_random_graphs_graphlets(self):
        raise NotImplemented()

    def clear_random_graphs_metrics(self):
        raise NotImplemented()

    """----- Listing and Loading Interfaces -----"""

    def list_entries(self):
        raise NotImplemented()

    def load_graphlets(self):
        raise NotImplemented()

    def load_metrics(self):
        raise NotImplemented()

    def load_random_graphs(self):
        raise NotImplemented()

    def load_random_graph_graphlets(self):
        raise NotImplemented()

    def load_random_graph_metrics(self):
        raise NotImplemented()
