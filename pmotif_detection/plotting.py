import networkx as nx
import pandas as pd
import json

from pmotifs.PMotifGraph import PMotifGraph


def get_kamada_kawai_layout(pmotif_graph: PMotifGraph):
    if not (pmotif_graph.output_directory / "kamada_kawai_layout.json").is_file():
        nx_g = pmotif_graph.load_graph()
        pos = _prepare_kamada_kawai_layout_with_multiple_components(nx_g)

        # Cast nd-Array type (from coords) to json serializable list
        pos = {k: list(v) for k, v in pos.items()}

        with open(pmotif_graph.output_directory / "kamada_kawai_layout.json", "w") as f:
            json.dump(pos, f)

    with open(pmotif_graph.output_directory / "kamada_kawai_layout.json", "r") as f:
        return json.load(f)


def _prepare_kamada_kawai_layout_with_multiple_components(nx_g):
    pos_df = pd.DataFrame(index=nx_g.nodes(), columns=nx_g.nodes())
    max_dist = -1
    for row, data in nx.shortest_path_length(nx_g):
        for col, dist in data.items():
            pos_df.loc[row, col] = dist
            max_dist = max(max_dist, dist)

    pos_df = pos_df.fillna(max_dist / 2 + 2)

    return nx.kamada_kawai_layout(nx_g, dist=pos_df.to_dict())


def highlight_motif(nx_g, motif, ax, pos):
    subgraph = nx.induced_subgraph(nx_g, motif)

    nx.draw_networkx_nodes(
        nx_g,
        nodelist=subgraph.nodes,
        node_color="r",
        pos=pos,
        ax=ax,
        node_size=20,
    )
    nx.draw_networkx_labels(
        nx_g,
        labels={node: node for node in subgraph.nodes},
        pos=pos,
        ax=ax,
        font_size=6,
        font_color="b",
    )
    nx.draw_networkx_edges(
        nx_g,
        pos=pos,
        edgelist=subgraph.edges,
        ax=ax,
        edge_color="r",
    )


def plot_graph_with_motif_highlight(nx_g, motifs, pos, ax, title=""):
    nx.draw(nx_g, pos=pos, ax=ax, node_size=20)

    for m in motifs:
        highlight_motif(nx_g, m, ax, pos)

    ax.set_title(title)


def get_zommed_graph(nx_g, nodes, node_range=3):
    relevant_nodes = []
    for n in nodes:
        neighbors = nx.descendants_at_distance(nx_g, n, node_range)
        relevant_nodes.extend(neighbors)
        relevant_nodes.append(n)

    subgraph = nx.induced_subgraph(nx_g, relevant_nodes)

    return subgraph
