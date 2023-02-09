from statistics import mean, stdev
from typing import List

from motif_position_tooling.utils.gtrieScannerUtils import parse_motif_analysis_results_table
from motif_position_tooling.utils.motif_io import MotifGraphWithRandomization
from motif_position_tooling.utils.motif_significance.freq_loader import get_all_motif_frequencies_of_randomized_graphs


def z_score(original_frequency: int, random_frequencies: List[int]) -> float:
    if stdev(random_frequencies) == 0:
        return -1
    return (original_frequency - mean(random_frequencies)) / stdev(random_frequencies)


def get_z_scores_for_motifs(motif_graph: MotifGraphWithRandomization, motif_size: int):
    original_motif_freq = parse_motif_analysis_results_table(motif_graph.get_motif_freq_file(motif_size), motif_size)
    randomized_frequencies = get_all_motif_frequencies_of_randomized_graphs(motif_graph, motif_size)

    return {
        motif_id: z_score(
            original_motif_freq[motif_id],
            randomized_frequencies.get(motif_id, [0] * len(motif_graph.swapped_graphs))
        )
        for motif_id in original_motif_freq
    }
