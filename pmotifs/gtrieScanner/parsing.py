"""Utility to read gtrieScanner output."""
from pathlib import Path
from typing import Dict


def parse_graphlet_detection_results_table(
    frequency_filepath: Path, k: int
) -> Dict[str, int]:
    """Load a graphlet frequency file created by gtrieScanner
    Return a lookup from graphlet-class (adj-matrix) to the number of graphlet-occurrences
    """
    with open(frequency_filepath, "r", encoding="utf-8") as frequency_file:
        lines = frequency_file.readlines()
    table_lines = lines[lines.index("Motif Analysis Results\n") + 2 :]

    header = table_lines.pop(0)
    del header

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
        _, *graphlet_class_parts = table_lines[i : i + table_row_height]

        # Separate last part into graph part and metric part
        frequency = graphlet_class_parts[-1].split("|")[0].split(" ")[-2]
        graphlet_class_parts[-1] = graphlet_class_parts[-1].split(" ")[0]

        graphlet_class = " ".join(map(lambda s: s.strip(), graphlet_class_parts))

        frequencies[graphlet_class] = int(frequency)

    return frequencies
