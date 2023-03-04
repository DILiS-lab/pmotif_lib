import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import tqdm


@dataclass
class GraphletPositionalMetrics:
    """Keeps track of metrics calculated from one graphlet occurrence"""
    degree: int
    anchor_node_distances: List[int]
    graph_module_participation: List[int]

    def to_json(self) -> str:
        return json.dumps({
            "degree": self.degree,
            "anchor_node_distances": self.anchor_node_distances,
            "graph_module_participation": self.graph_module_participation,
        })

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
    graphlet_metrics: List[GraphletPositionalMetrics]

    def save(self, outpath: Path):
        """Turn Results into multiple files, which can be read line by line and separately
        This is necessary as larger graphs result in object multiple gigabytes in size when stored as json or pickle"""

        if not outpath.is_dir():
            os.mkdir(outpath)

        with open(outpath / "anchor_nodes", "w") as f:
            for an in self.anchor_nodes:
                f.write(an)
                f.write("\n")

        with open(outpath / "graph_modules", "w") as f:
            for gm in self.graph_modules:
                f.write(" ".join(gm))
                f.write("\n")

        with open(outpath / "graphlet_metrics", "w") as f:
            for gm in self.graphlet_metrics:
                f.write(gm.to_json())
                f.write("\n")

        with open(outpath / "meta", "w") as f:
            json.dump({
                "anchor_nodes": len(self.anchor_nodes),
                "graph_modules": len(self.graph_modules),
                "graphlet_metrics": len(self.graphlet_metrics),
            }, f)

    @staticmethod
    def load(outpath: Path, supress_tqdm: bool = False):
        with open(outpath / "meta", "r") as f:
            file_lengths = json.load(f)

        anchor_nodes = []
        with open(outpath / "anchor_nodes", "r") as f:
            for l in tqdm.tqdm(
                f,
                desc="Loading Anchor Nodes",
                total=int(file_lengths["anchor_nodes"]),
                disable=supress_tqdm,
            ):
                anchor_nodes.append(l.strip())

        graph_modules = []
        with open(outpath / "graph_modules", "r") as f:
            for l in tqdm.tqdm(
                f,
                desc="Loading Graph Modules",
                total=int(file_lengths["graph_modules"]),
                disable=supress_tqdm,
            ):
                graph_modules.append(l.strip().split(" "))

        graphlet_metrics = []
        with open(outpath / "graphlet_metrics", "r") as f:
            for l in tqdm.tqdm(
                f,
                desc="Loading Graphlet Metrics",
                total=int(file_lengths["graphlet_metrics"]),
                disable=supress_tqdm,
            ):
                graphlet_metrics.append(
                    GraphletPositionalMetrics.from_json(json.loads(l))
                )

        return GraphPositionalMetrics(
            anchor_nodes=anchor_nodes,
            graph_modules=graph_modules,
            graphlet_metrics=graphlet_metrics,
        )
