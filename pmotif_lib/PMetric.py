from abc import ABC, abstractmethod
from typing import Any, Dict, List

import networkx as nx


class PMetric(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def pre_compute(self, graph: nx.Graph) -> Dict[str, Any]:
        """Pre-compute data from g.
        Result will be injected into the calculate method as `precompute_results` argument.
        Use this for expensive computations that you do not want to repeat for each subgraph occurrence such as
        shortest path, centrality, clustering calculations"""
        pass

    @abstractmethod
    def calculate(self, graph: nx.Graph, occurrence_nodes: List[int], precompute_results: Dict[str, Any]) -> Any:
        """Turns a given subgraph occurrence into a positional metric.
        Pre-computed data from `pre_compute` is available as `precompute_results`"""
        pass

    @abstractmethod
    def post_process(self, calculation_result: Any) -> Dict[str, float]:
        """Post-processes all results from `calculate`.
        Turns a positional metric into one or more positional evaluation metric(s).
        Has to return a dictionary, mapping a metric name to a float value.

        This method should be used to normalize the positional metric.
        It can also be used to turn one normalized positional metric into multiple evaluation metrics

        Return a dictionary mapping metric names to a metric value
        """
        pass
