import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import (
    List,
    Dict
)

import tqdm


@dataclass
class PositionalMetricMeta:
    """Keeps track on meta information about the graph and graph properties used in pos. metric calculation"""
    anchor_nodes: List[str]
    anchor_node_shortest_paths: Dict[str, Dict[str, int]]
    graph_modules: List[List[str]]

    def save(self, outpath: Path):
        """Turn Results into multiple files, which can be read line by line and separately
        This is necessary as larger graphs result in object multiple gigabytes in size when stored as json or pickle"""

        if not outpath.is_dir():
            os.mkdir(outpath)

        with open(outpath / "anchor_nodes", "w") as f:
            f.write(f"{len(self.anchor_nodes)}\n")
            for an in self.anchor_nodes:
                f.write(an)
                f.write("\n")

        with open(outpath / "anchor_node_shortest_paths", "w") as f:
            f.write(f"{len(self.anchor_nodes)}\n")
            for anchor_node, shortest_path_lookup in self.anchor_node_shortest_paths.items():
                f.write(f"{anchor_node} {json.dumps(shortest_path_lookup)}")
                f.write("\n")

        with open(outpath / "graph_modules", "w") as f:
            f.write(f"{len(self.graph_modules)}\n")
            for gm in self.graph_modules:
                f.write(" ".join(gm))
                f.write("\n")

    @staticmethod
    def _load_raw_dumped(name: str, outpath: Path, supress_tqdm: bool = False) -> List[str]:
        data = []
        with open(outpath / name, "r") as f:
            total = int(f.readline().strip())
            for line in tqdm.tqdm(
                f,
                desc=f"Loading {' '.join(name.split('_'))}",
                total=total,
                disable=supress_tqdm,
            ):
                data.append(line.strip())
        return data

    @staticmethod
    def _load_anchor_nodes(outpath: Path, supress_tqdm: bool = False):
        anchor_nodes_raw = PositionalMetricMeta._load_raw_dumped(
            "anchor_nodes",
            outpath,
            supress_tqdm,
        )
        return [an.strip() for an in anchor_nodes_raw]

    @staticmethod
    def _load_graph_modules(outpath: Path, supress_tqdm: bool = False):
        graph_modules_raw = PositionalMetricMeta._load_raw_dumped(
            "graph_modules",
            outpath,
            supress_tqdm,
        )
        return [gm.strip().split(" ") for gm in graph_modules_raw]

    @staticmethod
    def _load_anchor_nodes_shortest_paths(outpath: Path, supress_tqdm: bool = False):
        anchor_nodes_shortest_paths_raw = PositionalMetricMeta._load_raw_dumped(
            "anchor_node_shortest_paths",
            outpath,
            supress_tqdm,
        )
        shortest_path_lookup = {}
        for line in anchor_nodes_shortest_paths_raw:
            anchor_node, *jsonstring_parts = line.split(" ")
            jsonstring = " ".join(jsonstring_parts)
            shortest_path_lookup[anchor_node] = json.loads(jsonstring)
        return shortest_path_lookup

    @staticmethod
    def load(outpath: Path, supress_tqdm: bool = False):
        return PositionalMetricMeta(
            anchor_nodes=PositionalMetricMeta._load_anchor_nodes(
                outpath, supress_tqdm),
            anchor_node_shortest_paths=PositionalMetricMeta._load_anchor_nodes_shortest_paths(
                outpath, supress_tqdm),
            graph_modules=PositionalMetricMeta._load_graph_modules(
                outpath, supress_tqdm),
        )
