"""Class to encapsulate an induced subgraph and its isomorphic class."""
from dataclasses import dataclass
from typing import List


@dataclass
class GraphletOccurrence:
    """Keeps track of a graphlet occurrence"""

    graphlet_class: str
    nodes: List[str]

    @property
    def size(self):
        """Returns the size of the induced subgraph."""
        return len(self.nodes)

    def __hash__(self):
        return hash((self.graphlet_class, tuple(self.nodes)))

    def __eq__(self, other):
        return self.graphlet_class == other.graphlet_class and self.nodes == other.nodes
