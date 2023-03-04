from multiprocessing import Pool
from pathlib import Path
from typing import (
    Tuple,
    Dict
)

import pandas as pd
from tqdm import tqdm

from pmotifs.PMotifGraph import (
    PMotifGraph,
    PMotifGraphWithRandomization
)
from pmotifs.config import WORKERS


def load_results(
    GRAPH_EDGELIST: Path,
    OUT: Path,
    GRAPHLET_SIZE: int,
    supress_tqdm: bool = False,
) -> Tuple[PMotifGraph, pd.DataFrame]:
    g = PMotifGraph(GRAPH_EDGELIST, OUT)
    return g, _load_pgraph_data(g, GRAPHLET_SIZE, supress_tqdm)


def _load_pgraph_data(pgraph: PMotifGraph, graphlet_size: int, supress_tqdm: bool = False):
    g_p = pgraph.load_graphlet_pos_zip(graphlet_size, supress_tqdm)
    g_pm = pgraph.load_positional_data(graphlet_size, supress_tqdm)
    graphlet_lookup = dict(zip(g_p, g_pm.graphlet_metrics))

    df = pd.DataFrame([
        {**k.__dict__, **v.__dict__}
        for k, v in graphlet_lookup.items()
    ])
    return df


def load_randomized_results(
    pmotif_graph: PMotifGraph,
    graphlet_size: int,
    supress_tqdm: bool = False,
) -> Dict[PMotifGraph, pd.DataFrame]:
    pmotif_with_rand = PMotifGraphWithRandomization(
        pmotif_graph.edgelist_path,
        pmotif_graph.output_directory
    )

    input_args = [(swapped_graph, graphlet_size, supress_tqdm) for swapped_graph in pmotif_with_rand.swapped_graphs]

    with Pool(processes=WORKERS) as p:
        pbar = tqdm(
            input_args,
            total=len(pmotif_with_rand.swapped_graphs),
            desc="Loading Randomized Results",
        )
        randomized_results = p.starmap(
            _load_pgraph_data,
            pbar,
            chunksize=1,
        )

    return dict(zip(pmotif_with_rand.swapped_graphs, randomized_results))
