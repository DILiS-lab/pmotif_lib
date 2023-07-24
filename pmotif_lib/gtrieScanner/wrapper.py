"""Utility to call a gtrieScanner executable from python."""
# gtrieScanner violates snake_case, but is the official name of the wrapped utility
# For complete wrapping, the argument count needs to stay the same
# Therefore, we exclude those cases from py-linting:
# pylint: disable=invalid-name, too-many-arguments
import os
from pathlib import Path
from subprocess import Popen, PIPE
import zipfile

from pmotif_lib.gtrieScanner.graph_io import read_edgelist


def run_gtrieScanner(
    graph_edgelist: Path,
    graphlet_size: int,
    output_directory: Path,
    gtrieScanner_executable: str,
    directed: bool = False,
    with_weights: bool = True,
):
    """
    Detects motifs for the given edge list and compresses the result
    """
    out_dir = output_directory / str(graphlet_size)
    os.makedirs(out_dir)

    graph = read_edgelist(graph_edgelist)

    if "0" in graph.nodes:
        raise IndexError(
            "Network contains a node with index 0! "
            "gtrieScanner only accepts node indices starting from 1!"
        )

    # Build GTrieScanner command
    directed_arg = "-d" if directed else "-u"
    format_arg = "simple_weight" if with_weights else "simple"

    command_parts = [
        f"{gtrieScanner_executable}",
        "-s",
        graphlet_size,
        "-f",
        format_arg,
        "-g",
        graph_edgelist,
        directed_arg,
        "-oc",
        out_dir / "motif_pos",
        "-o",
        out_dir / "motif_freq",
    ]
    command_parts = [str(p) for p in command_parts]

    # Run gtrieScanner
    with Popen(
        command_parts,
        stdout=PIPE,
        stderr=PIPE,
    ) as p:
        p.wait()

    # Store motifs in max compressed zip for space efficiency
    with zipfile.ZipFile(
        f"{output_directory / str(graphlet_size) / 'motif_pos.zip'}", "w"
    ) as zipf:
        zipf.write(
            f"{output_directory / str(graphlet_size) / 'motif_pos'}",
            compress_type=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            arcname="motif_pos",
        )
    os.remove(output_directory / str(graphlet_size) / "motif_pos")
