"""Pre-Implemented PMetric to calculate the degree of a graphlet."""
from typing import List
import networkx as nx

from pmotif_lib.p_metric.p_metric import PMetric, PreComputation


class PDegree(PMetric):
    """Measures the degree of a graphlet.
    Graphlet degree is defined as the number of edges connecting a graphlet node to a non-graphlet
    node."""

    def __init__(self):
        super().__init__("pDegree")

    def metric_calculation(
        self,
        graph: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> int:
        """Counts each unique edge going
        from nodes within the graphlet to nodes outside the graphlet,
        or vice versa."""
        nodes = set(graphlet_nodes)
        all_edges = graph.edges(graphlet_nodes)
        external_degree = 0
        for src, dst in all_edges:
            if src in nodes and dst in nodes:
                # Edge within motif
                continue
            external_degree += 1
        return external_degree

    def pre_computation(self, graph: nx.Graph) -> PreComputation:
        """No pre-computation necessary for degree calculation"""
        return {}
