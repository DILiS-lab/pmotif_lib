from dataclasses import dataclass
from typing import List, Dict

from pmotifs.utils.GraphletOccurence import GraphletOccurrence


@dataclass
class GraphletPositionalMetrics:
    """Keeps track of metrics calculated from one graphlet occurrence"""
    degree: int
    anchor_node_distances: List[int]
    graph_module_participation: List[int]


@dataclass
class GraphPositionalMetrics:
    """Keeps track of positional metrics calculated in relation to one graph with anchor and module configuration"""
    anchor_nodes: List[str]
    graph_modules: List[List[str]]
    graphlet_metrics: Dict[GraphletOccurrence, GraphletPositionalMetrics]
