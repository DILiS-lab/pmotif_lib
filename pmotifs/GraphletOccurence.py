from math import sqrt
from dataclasses import dataclass
from typing import List


@dataclass
class GraphletOccurrence:
    """Keeps track of a graphlet occurrence"""

    graphlet_class: str
    nodes: List[str]

    @property
    def size(self):
        return int(sqrt(len(self.graphlet_class)))

    def __hash__(self):
        return hash((self.graphlet_class, tuple(self.nodes)))

    def __eq__(self, other):
        return self.graphlet_class == other.graphlet_class and self.nodes == other.nodes
