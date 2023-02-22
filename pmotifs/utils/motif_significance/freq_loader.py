"""Calculate Significance of Motifs in a given RandomizedMotifgraph"""
from typing import List, Dict

from pmotifs.utils.motif_io import PMotifGraphWithRandomization, PMotifGraph
from pmotifs.gtrieScanner import parse_motif_analysis_results_table


def get_all_motif_frequencies_of_randomized_graphs(
    g: PMotifGraphWithRandomization,
    k: int,
) -> Dict[str, List[int]]:
    """Concat all frequencies of the random graphs of the given MotifGraphWithRandomization into a lookup"""
    return get_all_motif_frequencies_of_graphs(
        g.swapped_graphs,
        k,
    )


def get_all_motif_frequencies_of_graphs(
        graphs: List[PMotifGraph],
        k: int,
) -> Dict[str, List[int]]:
    """Concat all frequencies of the given MotifGraphs into a lookup"""
    frequencies = {}
    for g in graphs:
        _f = parse_motif_analysis_results_table(
            g.get_graphlet_freq_file(k),
            k,
        )
        for motif_id, freq in _f.items():
            if motif_id not in frequencies:
                frequencies[motif_id] = []
            frequencies[motif_id].append(freq)

    # Not all motif ids occur in every graph
    # This means we have to do padding with 0s
    # if the count of frequencies we get  on a motif_id
    # is not equal to the count of graphs where
    # frequency was computed.
    # Otherwise, averages fail
    # Example: Imagine motif_x only occurs in one graph
    # and occurs y times
    # frequencies[motif_x] = [y]
    # therefore, the average would be y as well, despite
    # the fact, that it should be much lower (mean([0,y,0,...]))
    # WARNING: This does not preserve order in any way
    for k in frequencies:
        diff = len(graphs) - len(frequencies[k])
        frequencies[k] += [0] * diff
    return frequencies

