from __future__ import annotations

import os
from multiprocessing import Pool
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

from pmotifs.PMotifGraph import (
    PMotifGraph,
    PMotifGraphWithRandomization
)
from pmotifs.config import WORKERS
from pmotifs.pMetrics.PMetricResult import PMetricResult


class Result:
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

        self._p_metric_result_lookup = {
            r.metric_name: r
            for r in self.p_metric_results
        }

    def get_p_metric_result(self, name: str) -> PMetricResult:
        return self._p_metric_result_lookup[name]

    @staticmethod
    def load_result(
        GRAPH_EDGELIST: Path,
        OUT: Path,
        GRAPHLET_SIZE: int,
        supress_tqdm: bool = False,
    ) -> Result:
        """Loads results by building a pgraph from input args"""
        pgraph = PMotifGraph(GRAPH_EDGELIST, OUT)
        return Result._load_result(pgraph, GRAPHLET_SIZE, supress_tqdm)

    @staticmethod
    def _load_result(pgraph: PMotifGraph, graphlet_size: int, supress_tqdm: bool) -> Result:
        """Loads results for a given pgraph"""
        g_p = pgraph.load_graphlet_pos_zip(
            graphlet_size,
            supress_tqdm
        )

        pmetric_output_directory = pgraph.get_pmetric_directory(graphlet_size)

        p_metric_results = [
            PMetricResult.load_from_disk(pmetric_output_directory / content)
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

        return Result(
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
    ) -> List[Result]:
        pmotif_with_rand = PMotifGraphWithRandomization(
            pmotif_graph.edgelist_path,
            pmotif_graph.output_directory
        )

        input_args = [(swapped_graph, graphlet_size, supress_tqdm) for swapped_graph in pmotif_with_rand.swapped_graphs]

        with Pool(
            processes=WORKERS
        ) as p:
            pbar = tqdm(
                input_args,
                total=len(
                    pmotif_with_rand.swapped_graphs
                ),
                desc="Loading Randomized Results",
            )
            return p.starmap(
                Result._load_result,
                pbar,
                chunksize=1,
            )
