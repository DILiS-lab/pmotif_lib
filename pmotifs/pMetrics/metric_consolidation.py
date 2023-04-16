"""Contains pre-implemented consolidation methods for the pre-implemented PMetrics."""
from statistics import mean
from typing import List, Dict, Tuple

from pmotifs.analysis_utilities.Result import ConsolidationMethod
from pmotifs.pMetrics.PAnchorNodeDistance import PAnchorNodeDistance
from pmotifs.pMetrics.PDegree import PDegree
from pmotifs.pMetrics.PGraphModuleParticipation import PGraphModuleParticipation
from pmotifs.pMetrics.PMetric import RawMetric, PreComputation


def degree_consolidation(raw_metric: RawMetric, pre_compute: PreComputation) -> float:
    del pre_compute
    return raw_metric


def max_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    return max(_get_normalized_anchor_hop_distances(raw_metric, pre_compute))


def min_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    return min(_get_normalized_anchor_hop_distances(raw_metric, pre_compute))


def mean_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    return mean(_get_normalized_anchor_hop_distances(raw_metric, pre_compute))


def _get_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> List[float]:
    anchor_nodes = pre_compute["anchor_nodes"]
    closeness_centrality = pre_compute["closeness_centrality"]

    return [
        raw_metric[i] / closeness_centrality[anchor_node]
        for i, anchor_node in enumerate(anchor_nodes)
    ]


def graph_module_participation_ratio(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    total_module_count = len(pre_compute["graph_modules"])
    return len(raw_metric) / total_module_count


metrics: Dict[str, List[Tuple[str, ConsolidationMethod]]] = {
    # PAnchorNodeDistance evaluation metrics and their consolidation methods
    PAnchorNodeDistance().name: [
        ("max normalized anchor hop distance", max_normalized_anchor_hop_distances),
        ("min normalized anchor hop distance", min_normalized_anchor_hop_distances),
        ("mean normalized anchor hop distance", mean_normalized_anchor_hop_distances),
    ],
    # PGraphModuleParticipation evaluation metrics and their consolidation methods
    PGraphModuleParticipation().name: [
        ("graph module participation ratio", graph_module_participation_ratio)
    ],
    # PDegree evaluation metrics and their consolidation methods
    PDegree().name: [("degree", degree_consolidation)],
}
