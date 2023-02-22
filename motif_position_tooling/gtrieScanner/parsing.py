from pathlib import Path
from typing import Dict


def parse_motif_analysis_results_table(frequency_file: Path, k: int) -> Dict[str, int]:
    """Load a motif frequency file created by gtrieScanner
    Return a lookup from motif-class-id (adj-matrix) to the number of motif-occurrences"""
    with open(frequency_file, "r") as f:
        lines = f.readlines()
    table_lines = lines[lines.index("Motif Analysis Results\n") + 2:]

    header = table_lines.pop(0)

    # remove trailing newlines
    while table_lines[-1] == "\n":
        table_lines.pop(-1)

    frequencies = {}
    # Each table row contains a newline followed by a lien by line
    # printed adj. matrix with the shape k*k.
    # The last line of the matrix also contains some metrics
    # So we process k+1 lines batches, to process each row
    table_row_height = k + 1
    for i in range(0, len(table_lines), table_row_height):
        _, *motif_id_parts = table_lines[i:i + table_row_height]

        # Separate last part into graph part and metric part
        frequency = motif_id_parts[-1].split("|")[0].split(" ")[-2]
        motif_id_parts[-1] = motif_id_parts[-1].split(" ")[0]

        motif_id = " ".join(map(lambda s: s.strip(), motif_id_parts))

        frequencies[motif_id] = int(frequency)

    return frequencies
