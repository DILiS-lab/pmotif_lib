"""Handle the disk storing and loading of PMetric calculations (pre-compute and results)."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from tqdm import tqdm

from pmotif_lib.p_metric.p_metric import PreComputation, RawMetric


@dataclass
class PMetricResult:
    """Stores and loads PMetrics to disk. Creates a directory for each metric,
    containing the `graphlet_metrics` in a file, and a subdirectory `pre_compute`,
    with a file for each pre-compute key. Uses json and utf-8."""

    metric_name: str
    pre_compute: PreComputation
    graphlet_metrics: List[RawMetric]

    def save_to_disk(self, output: Path):
        """Stores pre_calculations to a specific path."""
        if output.name != self.metric_name:
            output = output / self.metric_name

        # Store pre_compute
        os.makedirs(output / "pre_compute")
        for pre_compute_name, pre_compute_value in self.pre_compute.items():
            pre_compute_filepath = output / "pre_compute" / pre_compute_name
            with open(pre_compute_filepath, "w", encoding="utf-8") as pre_compute_file:
                json.dump(pre_compute_value, pre_compute_file)

        # Store graphlet_metrics
        with open(
            output / "graphlet_metrics", "w", encoding="utf-8"
        ) as graphlet_metrics_file:
            graphlet_metrics_file.write(
                f"{len(self.graphlet_metrics)}\n"
            )  # Write len of file for progress bar total
            for g_m in self.graphlet_metrics:
                graphlet_metrics_file.write(json.dumps(g_m))
                graphlet_metrics_file.write("\n")

    @staticmethod
    def load_from_disk(output: Path, supress_tqdm: bool = False):
        """Loads metric results stored at output."""
        return PMetricResult(
            metric_name=output.name,
            pre_compute=PMetricResult._load_pre_compute(output / "pre_compute"),
            graphlet_metrics=PMetricResult._load_graphlet_metrics(
                output / "graphlet_metrics", supress_tqdm
            ),
        )

    @staticmethod
    def _load_pre_compute(pre_compute_dir: Path) -> PreComputation:
        """Loads all pre_compute values found at pre_compute_dir"""
        pre_compute = {}
        for content in os.listdir(str(pre_compute_dir)):
            if not (pre_compute_dir / content).is_file():
                continue
            with open(
                pre_compute_dir / content, "r", encoding="utf-8"
            ) as pre_compute_file:
                pre_compute[content] = json.load(pre_compute_file)
        return pre_compute

    @staticmethod
    def _load_graphlet_metrics(
        graphlet_metrics_filepath: Path, supress_tqdm=False
    ) -> List[RawMetric]:
        """Loads the graphlet metrics found at graphlet_metric_file"""
        with open(
            graphlet_metrics_filepath, "r", encoding="utf-8"
        ) as graphlet_metrics_file:
            total = int(graphlet_metrics_file.readline().strip())
            pbar = tqdm(
                graphlet_metrics_file,
                desc=f"Loading graphlet metrics for {graphlet_metrics_filepath.parent.name}",
                total=total,
                disable=supress_tqdm,
            )
            return [json.loads(line) for line in pbar]
