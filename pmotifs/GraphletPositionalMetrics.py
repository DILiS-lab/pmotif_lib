from dataclasses import dataclass
from typing import List, Dict

from pmotifs.GraphletOccurence import GraphletOccurrence


@dataclass
class GraphletPositionalMetrics:
    """Keeps track of metrics calculated from one graphlet occurrence"""
    degree: int
    anchor_node_distances: List[int]
    graph_module_participation: List[int]

    def to_json(self):
        return {
            "degree": self.degree,
            "anchor_node_distances": self.anchor_node_distances,
            "graph_module_participation": self.graph_module_participation,
        }

    @staticmethod
    def from_json(json_object):
        return GraphletPositionalMetrics(
            degree=json_object["degree"],
            anchor_node_distances=json_object["anchor_node_distances"],
            graph_module_participation=json_object["graph_module_participation"],
        )


@dataclass
class GraphPositionalMetrics:
    """Keeps track of positional metrics calculated in relation to one graph with anchor and module configuration"""
    anchor_nodes: List[str]
    graph_modules: List[List[str]]
    graphlet_metrics: Dict[GraphletOccurrence, GraphletPositionalMetrics]

    def to_json(self):
        return {
            "anchor_nodes": self.anchor_nodes,
            "graph_modules": self.graph_modules,
            "graphlet_metrics": [
                {
                    "graphlet_occurrence": graphlet_occurrence.to_json(),
                    "graphlet_positional_metrics": graphlet_positional_metrics.to_json(),
                 }
                for graphlet_occurrence, graphlet_positional_metrics in self.graphlet_metrics.items()
            ],
        }

    @staticmethod
    def from_json(json_object):
        def decode_graphlet_metric_tuple(e):
            g_oc = GraphletOccurrence.from_json(e["graphlet_occurrence"])
            g_pm = GraphletPositionalMetrics.from_json(e["graphlet_positional_metrics"])
            return g_oc, g_pm

        return GraphPositionalMetrics(
            anchor_nodes=json_object["anchor_nodes"],
            graph_modules=json_object["graph_modules"],
            graphlet_metrics=dict([
                # TODO: Decode json object
                decode_graphlet_metric_tuple(graphlet_metric_tuple)
                for graphlet_metric_tuple in json_object["graphlet_metrics"]
            ]),
        )
