import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import (
    List, Dict, Any
)

from tqdm import tqdm


class GraphletPositionalMetrics:
    """Keeps track of metrics calculated from one graphlet occurrence"""
    def __init__(self, named_metrics: Dict[str, Any]):
        self._named_metrics = named_metrics

    def to_json(self) -> str:
        return json.dumps({name: m for name, m in self._named_metrics.items()})

    @staticmethod
    def from_json(json_string: str):
        return GraphletPositionalMetrics(json.loads(json_string))


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
