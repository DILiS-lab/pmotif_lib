from abc import abstractmethod, ABC
from typing import Any, Dict, List, TypeVar, Callable

import networkx as nx

RawMetric = TypeVar("RawMetric")
PreComputation = Dict[str, Any]


class PMetric(ABC):
    """
    Represent a positional metric which will be calculated for each graphlet occurrence individually.
    """

    EXISTING_METRIC_NAMES = set()

    def __init__(self, name):
        if name in PMetric.EXISTING_METRIC_NAMES:
            raise ValueError(f"Metric with name {name} already exists!")
        self._name = name

        self._post_processing_register: Dict[str, Callable[[RawMetric], float]] = {}

    @abstractmethod
    def pre_computation(self, g: nx.Graph) -> PreComputation:
        """Is called before any metric calculation on individual graphlets.
        Use this to pre-compute data needed in each metric calculation. This way, it will only be computed once.
        This can vastly speed up metric calculation.
        Common pre-computes could be all-pair-shortest-path lookup, hubs, or communities.

        Return value of this method is fed into `metric_calculation` and each registered `post_processing` method
        via the `pre_compute` argument
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
        Can return any value, but has to have a post_processing/normalization method registered to the same metric name
        """
        pass

    def register_post_processing(
        self,
        name: str,
        post_processing: Callable[[RawMetric, PreComputation], float],
    ):
        """Register a named method which is used to produce an evaluation metric from a positional metric.
        An evaluation metric is a single floating point number per graphlet occurrence.
        If no post_processing is registered, PMetric.name will be used as evaluation metric name, and no post_processing
        will be applied (equivalent to postprocessing with `lambda x: x`).
        If the `metric_calculation` results needs to be normalized and summarized, do this here.
        For example, if `metric_calculation` returns the distanced of a graphlet occurrence to hub nodes,
        the result is an array of distances. This method can then be used to normalize those distances and
        return, say, the mean of the distances (a single float).
        This method can also be used to create multiple evaluation metrics from one positional metric, by registering
        more than one post_processing. For example, instead of the mean of the distances, one could also register
        the max and the min distance.
        """
        if name in self._post_processing_register.keys():
            raise ValueError(f"There already is a post-processing registered with the name '{name}'")

        self._post_processing_register[name] = post_processing

    def post_process(self, metrics: List[RawMetric]) -> Dict[str, List[float]]:
        """Computes the evaluation metrics using all registered post-processing methods.
        If no post-processing methods are registered, returns metric name and unprocessed raw metrics"""
        if len(self._post_processing_register) == 0:
            return {self._name: [m for m in metrics]}

        result = {}
        for name, post_callback in self._post_processing_register.items():
            result[name] = [post_callback(m) for m in metrics]
        return result
