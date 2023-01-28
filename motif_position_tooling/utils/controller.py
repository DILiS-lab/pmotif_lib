import networkx as nx
import os
from subprocess import Popen, PIPE
from pathlib import Path
import argparse
import zipfile


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "motif detection controller",
        "A python interface to execute a given gtrieScanner instance with given parameters",
    )
    parser.add_argument("gtrieScanner_executable", type=Path)
    parser.add_argument("graph_edgelist", type=Path)
    parser.add_argument("output_directory", type=Path)

    parser.add_argument("-k", type=int, help="Motif Size [3,k]", dest="motif_size", required=True)

    parser.add_argument("-d", "--directed", action="store_true", dest="directed", default=False)

    args = parser.parse_args()
    gtrieScanner(
        graph_edgelist=args.graph_edgelist,
        motif_size=args.motif_size,
        output_directory=args.output_directory,
        gtrieScanner_executable=args.gtrieScanner_executable,
        directed=args.directed,
    )
