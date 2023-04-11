from typing import List

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

from pmotifs.pMetrics.PMetric import PMetric, PreComputation


class PGraphModuleParticipation(PMetric):

    def __init__(self):
        super().__init__("pGraphModuleParticipation")

    def pre_computation(self, g: nx.Graph) -> PreComputation:
        """Calculates graph modules with a greedy modularity approach"""
        return {"graph_modules": list(map(list, greedy_modularity_communities(g)))}

    def metric_calculation(
        self,
        g: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> List[int]:
        """Returns a list of indices indicating which modules contain nodes of the graphlet occurrence"""
        participations = []
        for i, p in enumerate(pre_compute["graph_modules"]):
            for node in graphlet_nodes:
                if node in p:
                    participations.append(i)
                    break
        return participations
