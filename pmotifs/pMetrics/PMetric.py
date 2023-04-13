from abc import abstractmethod, ABC
from typing import Any, Dict, List, TypeVar

import networkx as nx

RawMetric = TypeVar("RawMetric")
PreComputation = Dict[str, Any]


class PMetric(ABC):
    """
    Represent a positional metric which will be calculated for each graphlet occurrence individually.
    """

    EXISTING_METRIC_NAMES = set()

    def __init__(self, name: str):
        if name in PMetric.EXISTING_METRIC_NAMES:
            raise ValueError(f"Metric with name {name} already exists!")
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def pre_computation(self, g: nx.Graph) -> PreComputation:
        """Is called before any metric calculation on individual graphlets.
        Use this to pre-compute data needed in each metric calculation. This way, it will only be computed once.
        This can vastly speed up metric calculation.
        Common pre-computes could be all-pair-shortest-path lookup, hubs, or communities.

        Return value of this method is fed into the `metric_calculation` method via the `pre_compute` argument
        """
        pass

    @abstractmethod
    def metric_calculation(
        self,
        g: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> RawMetric:
        """Is called on each graphlet occurrence to compute the positional metric.
        Can return any type, but has to be json serializable
        """
        pass

