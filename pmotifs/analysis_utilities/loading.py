from pathlib import Path
from typing import Tuple

import pandas as pd

from pmotifs.PMotifGraph import PMotifGraph


def load_results(GRAPH_EDGELIST: Path, OUT: Path, GRAPHLET_SIZE: int) -> Tuple[PMotifGraph, pd.DataFrame]:
    g = PMotifGraph(GRAPH_EDGELIST, OUT)
    g_p = g.load_graphlet_pos_zip(GRAPHLET_SIZE)
    g_pm = g.load_positional_data(GRAPHLET_SIZE)
    graphlet_lookup = dict(zip(g_p, g_pm.graphlet_metrics))

    df = pd.DataFrame([
        {**k.__dict__, **v.__dict__}
        for k, v in graphlet_lookup.items()
    ])
    return g, df
