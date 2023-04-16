import statistics
from typing import List, Dict

import networkx as nx

from pmotifs.pMetrics.PMetric import PMetric, PreComputation


class PAnchorNodeDistance(PMetric):
    def __init__(self):
        super().__init__("pAnchorNodeDistance")

    @staticmethod
    def get_hubs(g: nx.Graph) -> List[str]:
        """Returns hubs of a networkx graph
        Nodes with a degree higher than one standard deviations above the mean degree are considered hubs
        """
        degrees = dict(g.degree)

        degree_mean = statistics.mean(degrees.values())
        degree_stdev = statistics.stdev(degrees.values())

        return [
            node
            for node, degree in degrees.items()
            if degree > degree_mean + degree_stdev
        ]

    def pre_computation(self, g: nx.Graph) -> PreComputation:
        """Pre-compute anchor nodes and their shortest paths lookup"""
        anchor_nodes = PAnchorNodeDistance.get_hubs(g)

        nodes_shortest_path_lookup = {
            anchor_node: nx.single_source_shortest_path_length(g, anchor_node)
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
        g: nx.Graph,
        graphlet_nodes: List[str],
        pre_compute: PreComputation,
    ) -> List[int]:
        """Calculates the shortest path from any node in the graphlet occurrence to each of the anchor nodes"""
        path_lengths = []

        anchor_node: str
        shortest_path_lookup: Dict[str, int]
        for anchor_node, shortest_path_lookup in pre_compute[
            "nodes_shortest_path_lookup"
        ].items():
            if anchor_node in graphlet_nodes:
                path_lengths.append(0)
                continue
            shortest_path = min(
                [shortest_path_lookup.get(n, -1) for n in graphlet_nodes]
            )

            path_lengths.append(shortest_path)
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
