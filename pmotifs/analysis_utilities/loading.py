from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

from pmotifs.PMotifGraph import (
    PMotifGraph,
    PMotifGraphWithRandomization
)
from pmotifs.PositionalMetricMeta import PositionalMetricMeta
from pmotifs.config import WORKERS


@dataclass
class Result:
    pmotif_graph: PMotifGraph
    positional_metric_df: pd.DataFrame
    positional_metric_meta: PositionalMetricMeta
    graphlet_size: int

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
        g_pm = pgraph.load_positional_metrics(
            graphlet_size,
            supress_tqdm
        )
        graphlet_lookup = dict(zip(g_p, g_pm.graphlet_metrics))

        positional_metric_df = pd.DataFrame(
            [
                {**k.__dict__, **v.__dict__}
                for k, v in graphlet_lookup.items()
            ]
        )

        positional_metric_meta = pgraph.load_positional_meta(
            graphlet_size,
            supress_tqdm
        )

        return Result(
            pmotif_graph=pgraph,
            positional_metric_df=positional_metric_df,
            positional_metric_meta=positional_metric_meta,
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
