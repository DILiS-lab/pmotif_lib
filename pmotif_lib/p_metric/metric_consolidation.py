"""Contains pre-implemented consolidation methods for the pre-implemented PMetrics."""
from statistics import mean
from typing import List, Dict, Tuple

from pmotif_lib.result_transformer import ConsolidationMethod
from pmotif_lib.p_metric.p_anchor_node_distance import PAnchorNodeDistance
from pmotif_lib.p_metric.p_degree import PDegree
from pmotif_lib.p_metric.p_graph_module_participation import PGraphModuleParticipation
from pmotif_lib.p_metric.p_metric import RawMetric, PreComputation


def degree_consolidation(raw_metric: RawMetric, pre_compute: PreComputation) -> float:
    """Consolidate PDegree. PDegree already is a single number per graphlet occurrence,
    no additional consolidation needed."""
    del pre_compute
    return raw_metric


def max_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    """Consolidate PAnchorNodeDistance. Normalize the distances by closeness centrality
    and return the highest distance."""
    distances = _get_normalized_anchor_hop_distances(raw_metric, pre_compute)
    if len(distances) == 0:
        return -1
    if len(distances) == 1:
        return distances[0]
    return max(distances)


def min_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    """Consolidate PAnchorNodeDistance. Normalize the distances by closeness centrality
    and return the lowest distance."""
    distances = _get_normalized_anchor_hop_distances(raw_metric, pre_compute)
    if len(distances) == 0:
        return -1
    if len(distances) == 1:
        return distances[0]
    return min(distances)


def mean_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    """Consolidate PAnchorNodeDistance. Normalize the distances by closeness centrality
    and return the mean distance."""
    distances = _get_normalized_anchor_hop_distances(raw_metric, pre_compute)
    if len(distances) == 0:
        return -1
    if len(distances) == 1:
        return distances[0]
    return mean(distances)


def _get_normalized_anchor_hop_distances(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> List[float]:
    """Normalize the distances by closeness centrality of the anchor nodes.
    Some nodes are more central than others, making such normalization necessary to make
    the distances to different anchors comparable.
    """
    anchor_nodes = pre_compute["anchor_nodes"]
    closeness_centrality = pre_compute["closeness_centrality"]

    return [
        raw_metric[i] / closeness_centrality[anchor_node]
        for i, anchor_node in enumerate(anchor_nodes)
    ]


def graph_module_participation_ratio(
    raw_metric: RawMetric, pre_compute: PreComputation
) -> float:
    """Consolidate PGraphModuleParticipation. Return a ratio of modules participated by the graphlet
    compared to all existing modules."""
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
