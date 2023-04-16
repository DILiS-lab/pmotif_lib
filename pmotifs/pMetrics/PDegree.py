from typing import List

import networkx as nx

from pmotifs.pMetrics.PMetric import PMetric, PreComputation


class PDegree(PMetric):
    def __init__(self):
        super().__init__("pDegree")

    def metric_calculation(
        self,
        g: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> int:
        """Counts each unique edge going from nodes within the graphlet to nodes outside the graphlet"""
        nodes = set(graphlet_nodes)
        all_edges = g.edges(graphlet_nodes)
        external_degree = 0
        for u, v in all_edges:
            if u in nodes and v in nodes:
                # Edge within motif
                continue
            external_degree += 1
        return external_degree

    def pre_computation(self, g: nx.Graph) -> PreComputation:
        """No pre-computation necessary for degree calculation"""
        return {}
