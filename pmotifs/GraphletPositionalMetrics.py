import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import (
    List
)

from tqdm import tqdm


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
    def from_json(json_string: str):
        json_object = json.loads(json_string)
        return GraphletPositionalMetrics(
            degree=json_object["degree"],
            anchor_node_distances=json_object["anchor_node_distances"],
            graph_module_participation=json_object["graph_module_participation"],
        )


@dataclass
class GraphPositionalMetrics:
    """Utility to save and load GraphletPositionalMetrics"""
    graphlet_metrics: List[GraphletPositionalMetrics]

    def save(self, outpath: Path):
        if not outpath.is_dir():
            os.mkdir(outpath)

        with open(outpath / "graphlet_metrics", "w") as f:
            f.write(f"{len(self.graphlet_metrics)}\n")
            for gm in self.graphlet_metrics:
                f.write(gm.to_json())
                f.write("\n")

    @staticmethod
    def load(outpath: Path, supress_tqdm: bool = False):
        with open(outpath / "graphlet_metrics", "r") as f:
            total = int(f.readline().strip())
            pbar = tqdm(
                f,
                desc="Loading graphlet metrics",
                total=total,
                disable=supress_tqdm,
            )
            return GraphPositionalMetrics(graphlet_metrics=[GraphletPositionalMetrics.from_json(line) for line in pbar])
