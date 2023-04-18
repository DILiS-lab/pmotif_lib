"""Pre-Implemented PMetric to calculate the number of graph modules a graphlet touches."""
from typing import List
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

from pmotif_lib.p_metric.p_metric import PMetric, PreComputation


class PGraphModuleParticipation(PMetric):
    """Measures how many unique graph modules a graphlet participates in.
    Graph modules are calculated using greedy modularity optimization.
    A graphlet participates in a module, if at least one graphlet node belongs to that module.
    """

    def __init__(self):
        super().__init__("pGraphModuleParticipation")

    def pre_computation(self, graph: nx.Graph) -> PreComputation:
        """Calculates graph modules with a greedy modularity approach."""
        return {"graph_modules": list(map(list, greedy_modularity_communities(graph)))}

    def metric_calculation(
        self,
        graph: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> List[int]:
        """Returns a list of indices
        indicating which modules contain nodes of the graphlet occurrence."""
        participations = []
        for i, graph_module in enumerate(pre_compute["graph_modules"]):
            for node in graphlet_nodes:
                if node in graph_module:
                    participations.append(i)
                    break
        return participations
