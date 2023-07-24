"""Utility to load results of previous (p)motif-detections from disk and transform the positional
metrics with consolidation methods into evaluation metrics."""
from __future__ import annotations
import os
from multiprocessing import Pool
from pathlib import Path
from typing import List, Callable
import pandas as pd
from tqdm import tqdm

from pmotif_lib.p_motif_graph import PMotifGraph, PMotifGraphWithRandomization
from pmotif_lib.p_metric.p_metric import RawMetric, PreComputation
from pmotif_lib.p_metric.p_metric_result import PMetricResult


ConsolidationMethod = Callable[[RawMetric, PreComputation], float]


class ResultTransformer:
    """Load raw graphlets and their positional metrics from disk and offers an interface to
    consolidate the positional metrics into new evaluation metrics."""

    def __init__(
        self,
        pmotif_graph: PMotifGraph,
        positional_metric_df: pd.DataFrame,
        p_metric_results: List[PMetricResult],
        graphlet_size: int,
    ):
        self.pmotif_graph: PMotifGraph = pmotif_graph
        self.positional_metric_df: pd.DataFrame = positional_metric_df
        self.p_metric_results: List[PMetricResult] = p_metric_results
        self.graphlet_size: int = graphlet_size

        self._p_metric_result_lookup = {r.metric_name: r for r in self.p_metric_results}

        self._consolidated_metrics: List[str] = []

    @property
    def consolidated_metrics(self) -> List[str]:
        """Return all consolidated metrics which were applied through `consolidate_metric`."""
        return self._consolidated_metrics

    def get_p_metric_result(self, name: str) -> PMetricResult:
        """Return the result stored under the metric name `name`.
        Raises a KeyError if no such metric was found on disk."""
        return self._p_metric_result_lookup[name]

    def consolidate_metric(
        self,
        metric_name: str,
        consolidate_name: str,
        consolidate_method: ConsolidationMethod,
    ):
        """Apply `consolidate_method` on the `metric_name` column,
        creating a new `consolidate_name` column.
        Feeds the pre-computation result and the raw metric into the `consolidate_method`.

        Expects `metric_name` to be a name of a metric in `self.p_metric_results`.
        """
        p_metric_result = self.get_p_metric_result(metric_name)

        self.positional_metric_df[consolidate_name] = self.positional_metric_df[
            metric_name
        ].apply(lambda x: consolidate_method(x, p_metric_result.pre_compute))
        self._consolidated_metrics.append(consolidate_name)

    @staticmethod
    def load_result(
        edgelist: Path,
        out: Path,
        graphlet_size: int,
        supress_tqdm: bool = False,
    ) -> ResultTransformer:
        """Load results by building a pgraph from input args."""
        pgraph = PMotifGraph(edgelist, out)
        return ResultTransformer._load_result(pgraph, graphlet_size, supress_tqdm)

    @staticmethod
    def _load_result(
        pgraph: PMotifGraph, graphlet_size: int, supress_tqdm: bool
    ) -> ResultTransformer:
        """Load results for a given pgraph from disk."""
        g_p = pgraph.load_graphlet_pos_zip(graphlet_size, supress_tqdm)

        pmetric_output_directory = pgraph.get_pmetric_directory(graphlet_size)

        p_metric_results = [
            PMetricResult.load_from_disk(
                pmetric_output_directory / content, supress_tqdm
            )
            for content in os.listdir(str(pmetric_output_directory))
            if (pmetric_output_directory / content).is_dir()
        ]

        graphlet_data = []
        for i, g_oc in enumerate(g_p):
            row = {"graphlet_class": g_oc.graphlet_class, "nodes": g_oc.nodes}
            for metric_result in p_metric_results:
                row[metric_result.metric_name] = metric_result.graphlet_metrics[i]
            graphlet_data.append(row)

        positional_metric_df = pd.DataFrame(graphlet_data)

        return ResultTransformer(
            pmotif_graph=pgraph,
            positional_metric_df=positional_metric_df,
            p_metric_results=p_metric_results,
            graphlet_size=graphlet_size,
        )

    @staticmethod
    def load_randomized_results(
        pmotif_graph: PMotifGraph,
        graphlet_size: int,
        supress_tqdm: bool = False,
        workers: int = 1,
    ) -> List[ResultTransformer]:
        """Loads `graphlet_size`-graphlets and computed metrics which are present on disk."""
        pmotif_with_rand = PMotifGraphWithRandomization(
            pmotif_graph.edgelist_path, pmotif_graph.output_directory
        )

        input_args = [
            (swapped_graph, graphlet_size, supress_tqdm)
            for swapped_graph in pmotif_with_rand.swapped_graphs
        ]

        with Pool(processes=workers) as pool:
            pbar = tqdm(
                input_args,
                total=len(pmotif_with_rand.swapped_graphs),
                desc="Loading Randomized Results",
            )
            return pool.starmap(
                ResultTransformer._load_result,
                pbar,
                chunksize=1,
            )
