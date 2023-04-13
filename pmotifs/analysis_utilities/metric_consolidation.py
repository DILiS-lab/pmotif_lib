from enum import Enum
from statistics import mean

from pmotifs.analysis_utilities.loading import Result


def get_degree(result: Result):
    return list(result.positional_metric_df["degree"])


def get_max_of_normalized_anchor_hop_distances(result: Result):
    return list(map(max, _get_normalized_anchor_hop_distances(result)))


def get_min_of_normalized_anchor_hop_distances(result: Result):
    return list(map(min, _get_normalized_anchor_hop_distances(result)))


def get_mean_of_normalized_anchor_hop_distances(result: Result):
    return list(map(mean, _get_normalized_anchor_hop_distances(result)))


def _get_normalized_anchor_hop_distances(
    result: Result
):
    # Normalization by Closeness Centrality
    anchor_nodes = result.get_p_metric_result("pAnchorNodeDistance").pre_compute["anchor_nodes"]
    closeness_centrality = result.get_p_metric_result("pAnchorNodeDistance").pre_compute["closeness_centrality"]

    def normalize_by_closeness_centrality(
        distances
    ):
        normalized = []
        for i, anchor_node in enumerate(
            anchor_nodes
        ):
            normalized.append(
                distances[i] / closeness_centrality[anchor_node]
                )
        return normalized

    normalized_col = result.positional_metric_df["anchor_node_distances"].apply(normalize_by_closeness_centrality)
    return list(normalized_col)


def get_graph_module_participation_ratio(result: Result):
    total_module_count = len(
        result.get_p_metric_result("pGraphModuleParticipation").pre_compute["graph_modules"]
    )
    ratio_col = result.positional_metric_df["graph_module_participation"].apply(
        lambda l: len(l) / total_module_count
    )
    return ratio_col


metrics = {
    "max normalized anchor hop distance": get_max_of_normalized_anchor_hop_distances,
    "min normalized anchor hop distance": get_min_of_normalized_anchor_hop_distances,
    "mean normalized anchor hop distance": get_mean_of_normalized_anchor_hop_distances,
    "graph module participation ratio": get_graph_module_participation_ratio,
    "degree": get_degree,
}
