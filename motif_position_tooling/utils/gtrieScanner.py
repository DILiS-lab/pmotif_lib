import networkx as nx
import os
from subprocess import Popen, PIPE
from pathlib import Path
import argparse
import zipfile
from typing import Dict


def gtrieScanner(graph_edgelist: Path, motif_size: int, output_directory: Path, gtrieScanner_executable: Path,
                 directed: bool = False):
    """
    Detects motifs for the given edge list and compresses the result
    """
    out_dir = output_directory / str(motif_size)
    os.makedirs(out_dir)

    # Make sure network is in gTrie-readable format
    g = nx.read_edgelist(
        str(graph_edgelist),
        data=False,
        create_using=nx.Graph,  # No repeated edges
    )
    g.remove_edges_from(nx.selfloop_edges(g))

    if "0" in g.nodes:
        raise IndexError(
            "Network contains a node with index 0! gtrieScanner only accepts node indices starting from 1!")

    # Build GTrieScanner command
    directed_arg = "-d" if directed else "-u"
    prefix = "./" if str(gtrieScanner_executable)[0] not in ["/", "."] else ""

    command_parts = [
        f"{prefix}{gtrieScanner_executable}",
        "-s", motif_size,
        "-f", "simple",
        "-g", graph_edgelist,
        directed_arg,
        "-oc", out_dir / "motif_pos",
        "-o", out_dir / "motif_freq",
    ]
    command_parts = [str(p) for p in command_parts]

    # Run gtrieScanner
    p = Popen(
        command_parts,
        stdout=PIPE,
        stderr=PIPE,
    )
    p.wait()

    # Store motifs in max compressed zip for space efficiency
    with zipfile.ZipFile(f"{output_directory / str(motif_size) / 'motif_pos.zip'}", "w") as zipf:
        zipf.write(
            f"{output_directory / str(motif_size) / 'motif_pos'}",
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            arcname="motif_pos",
        )
    os.remove(output_directory / str(motif_size) / 'motif_pos')


def parse_motif_analysis_results_table(frequency_file: Path, k: int) -> Dict[str, int]:
    """Load a motif frequency file created by gtrieScanner"""
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
