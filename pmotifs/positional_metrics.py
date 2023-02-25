"""This utility takes a network and nodes (or supernodes)
and calculates various positional metrics for those inputs"""
import statistics
from typing import List, Callable, Dict
from tqdm import tqdm
from multiprocessing import Pool
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

from pmotifs.GraphletOccurence import GraphletOccurrence
from pmotifs.GraphletPositionalMetrics import GraphletPositionalMetrics, GraphPositionalMetrics
from pmotifs.PMotifGraph import PMotifGraph
from pmotifs.config import WORKERS


def get_hubs(g: nx.Graph) -> List[str]:
    # We define a hub as a node with a degree one stdev abiove the avg
    """Returns hubs of a networkx graph
    Nodes with a degree higher than one standard deviations above the mean degree are considered hubs"""
    degrees = dict(g.degree)

    degree_mean = statistics.mean(degrees.values())
    degree_stdev = statistics.stdev(degrees.values())

    return [
        node
        for node, degree in degrees.items()
        if degree > degree_mean + degree_stdev
    ]


def get_modularity_communities(g: nx.Graph) -> List[List[str]]:
    return list(map(list, greedy_modularity_communities(g)))


def get_group_betweenness(g: nx.Graph, node_groups: List[List[str]]) -> List[float]:
    return nx.group_betweenness_centrality(g, node_groups)


def get_group_degree(g: nx.Graph, group: List[str]) -> int:
    nodes = set(group)
    all_edges = g.edges(group)
    external_degree = 0
    for (u, v) in all_edges:
        if u in nodes and v in nodes:
            # Edge within motif
            continue
        external_degree += 1
    return external_degree


def graphlet_occurrence_distance_to_nodes(
        nodes_shortest_path_lookup: Dict[str, Dict[str, int]],
        group: List[str],
):
    path_lengths = []

    anchor_node: str
    shortest_path_lookup: Dict[str, int]
    for anchor_node, shortest_path_lookup in nodes_shortest_path_lookup.items():
        if anchor_node in group:
            path_lengths.append(0)
            continue
        shortest_path = min([shortest_path_lookup.get(n, -1) for n in group])

        path_lengths.append(shortest_path)
    return path_lengths


def graphlet_occurrence_module_participation(modules: List[List[str]], graphlet_oc: List[str]):
    participations = []
    for i, p in enumerate(modules):
        for node in graphlet_oc:
            if node in p:
                participations.append(i)
                break
    return participations


def single_arg_wrapper_create_graphlet_positional_metrics(args):
    return create_graphlet_positional_metrics(*args)


def create_graphlet_positional_metrics(
        g: nx.Graph,
        graphlet_occurrence: GraphletOccurrence,
        nodes_shortest_path_lookup: Dict[str, Dict[str, int]],
        graph_modules: List[List[str]],
) -> GraphletPositionalMetrics:
    return GraphletPositionalMetrics(
        degree=get_group_degree(
            g, graphlet_occurrence.nodes
        ),
        anchor_node_distances=graphlet_occurrence_distance_to_nodes(
            nodes_shortest_path_lookup, graphlet_occurrence.nodes
        ),
        graph_module_participation=graphlet_occurrence_module_participation(
            graph_modules, graphlet_occurrence.nodes
        ),
    )


def process_graphlet_occurrences(
    g: nx.Graph,
    graphlet_occurrences: List[GraphletOccurrence],
    anchor_nodes_generator: Callable[[nx.Graph], List[str]] = get_hubs,
    graph_modules_generator: Callable[[nx.Graph], List[List[str]]] = get_modularity_communities,
) -> GraphPositionalMetrics:
    """Calculate motif positional metrics"""

    anchor_nodes = anchor_nodes_generator(g)
    nodes_shortest_path_lookup = {
        anchor_node: nx.single_source_shortest_path_length(g, anchor_node)
        for anchor_node in anchor_nodes
    }

    graph_modules = graph_modules_generator(g)

    positional_metrics: List[GraphletPositionalMetrics] = []

    with Pool(processes=WORKERS) as p:
        with tqdm(
            total=len(graphlet_occurrences),
            desc="Calculating Positional Metrics for Graphlet Occurrences",
        ) as pbar:
            for g_pm in p.imap(
                    single_arg_wrapper_create_graphlet_positional_metrics,
                    [(g, _g_oc, nodes_shortest_path_lookup, graph_modules) for _g_oc in graphlet_occurrences],
                    chunksize=100,
            ):
                positional_metrics.append(g_pm)
                pbar.update()

    return GraphPositionalMetrics(
        anchor_nodes=anchor_nodes,
        graph_modules=graph_modules,
        graphlet_metrics=positional_metrics,
    )


def calculate_metrics(
    pmotif_graph: PMotifGraph,
    graphlet_size: int,
    anchor_nodes_generator: Callable[[nx.Graph], List[str]] = get_hubs,
    graph_modules_generator: Callable[[nx.Graph], List[List[str]]] = get_modularity_communities,
) -> GraphPositionalMetrics:
    """When pointed to a graph and a motif file, unzips the motif file, reads the graph and calculates various
    positional metrics"""
    print("Reading Graph")
    g = nx.readwrite.edgelist.read_edgelist(pmotif_graph.get_graph_path(), data=False, create_using=nx.Graph)
    print("Loading Graphlet Occurrences")
    graphlet_occurrences: List[GraphletOccurrence] = pmotif_graph.load_graphlet_pos_zip(graphlet_size)
    print("Processing Graphlet Occurrences")
    return process_graphlet_occurrences(g, graphlet_occurrences, anchor_nodes_generator, graph_modules_generator)
