import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from tqdm import tqdm

from pmotifs.pMetrics.PMetric import PreComputation, RawMetric


@dataclass
class PMetricResult:
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
            with open(output / "pre_compute" / pre_compute_name, "w") as f:
                json.dump(pre_compute_value, f)

        # Store graphlet_metrics
        with open(output / "graphlet_metrics", "w") as f:
            f.write(
                f"{len(self.graphlet_metrics)}\n"
            )  # Write len of file for progress bar total
            for g_m in self.graphlet_metrics:
                f.write(json.dumps(g_m))
                f.write("\n")

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
            with open(pre_compute_dir / content, "r") as f:
                pre_compute[content] = json.load(f)
        return pre_compute

    @staticmethod
    def _load_graphlet_metrics(
        graphlet_metric_file: Path, supress_tqdm=False
    ) -> List[RawMetric]:
        """Loads the graphlet metrics found at graphlet_metric_file"""
        with open(graphlet_metric_file, "r") as f:
            total = int(f.readline().strip())
            pbar = tqdm(
                f,
                desc=f"Loading graphlet metrics for {graphlet_metric_file.parent.name}",
                total=total,
                disable=supress_tqdm,
            )
            return [json.loads(line) for line in pbar]
