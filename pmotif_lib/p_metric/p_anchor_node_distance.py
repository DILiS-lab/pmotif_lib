"""Pre-Implemented PMetric to calculate the distance of a graphlet to network hubs."""
import statistics
from typing import List, Dict

import networkx as nx

from pmotif_lib.p_metric.p_metric import PMetric, PreComputation


class PAnchorNodeDistance(PMetric):
    """Measures the distance of a graphlet to anchor nodes.
    Anchor nodes are defined as hubs of the network (see `get_hubs`).
    The distance of a graphlet to a node is defined as the smallest distance between any
    node of the graphlet to the anchor node."""

    def __init__(self):
        super().__init__("pAnchorNodeDistance")

    @staticmethod
    def get_hubs(graph: nx.Graph) -> List[str]:
        """Return hubs of a networkx graph. Nodes with a degree higher than one standard deviations
        above the mean degree are considered hubs.
        """
        degrees = dict(graph.degree)

        degree_mean = statistics.mean(degrees.values())
        degree_stdev = statistics.stdev(degrees.values())

        return [
            node
            for node, degree in degrees.items()
            if degree > degree_mean + degree_stdev
        ]

    def pre_computation(self, graph: nx.Graph) -> PreComputation:
        """Pre-compute anchor nodes and their shortest paths lookup"""
        anchor_nodes = PAnchorNodeDistance.get_hubs(graph)

        nodes_shortest_path_lookup = {
            anchor_node: nx.single_source_shortest_path_length(graph, anchor_node)
            for anchor_node in anchor_nodes
        }

        closeness_centrality = {
            anchor_node: statistics.mean(shortest_path_lookup.values())
            for anchor_node, shortest_path_lookup in nodes_shortest_path_lookup.items()
        }

        return {
            "anchor_nodes": anchor_nodes,
            "nodes_shortest_path_lookup": nodes_shortest_path_lookup,
            "closeness_centrality": closeness_centrality,
        }

    def metric_calculation(
        self,
        graph: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> List[int]:
        """Calculate the shortest path from any node in the graphlet occurrence
        to each of the anchor nodes."""
        path_lengths = []

        shortest_path_lookup: Dict[str, int]
        for shortest_path_lookup in pre_compute["nodes_shortest_path_lookup"].values():
            distances = [
                shortest_path_lookup[node]
                for node in graphlet_nodes
                if node in shortest_path_lookup
            ]
            # A graphlet is assumed to always be connected
            # Therefore, there either is a path to an anchor node from each graphlet node,
            # or no path from either graphlet node.
            # Also, the distance between nodes can be at minimum 0 (if the nodes are identical).
            # Therefore, if we can not find any distance, we set it to -1, symbolizing "unreachable"
            if len(distances) == 0:
                distances = [-1]

            path_lengths.append(min(distances))
        return path_lengths

    @staticmethod
    def get_normalized_anchor_hop_distances(
        metric: List[int],
        pre_compute,
    ):
        """Normalize distances by closeness centrality"""
        anchor_nodes = pre_compute["anchor_nodes"]
        closeness_centrality = pre_compute["closeness_centrality"]
        return [
            metric[i] / closeness_centrality[anchor_node]
            for i, anchor_node in enumerate(anchor_nodes)
        ]
