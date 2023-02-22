"""This utility takes a network and nodes (or supernodes)
and calculates various positional metrics for those inputs"""
import statistics
from pathlib import Path
from typing import List, Callable, Dict
from tqdm import tqdm
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from motif_position_tooling.utils.motif_io import MotifGraph


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


def motif_distance_to_nodes(g: nx.Graph, anchor_nodes: List[str], motif: List[str]):

    nodes_shortest_path_lookup = {
        anchor_node: nx.single_source_shortest_path_length(g, anchor_node)
        for anchor_node in anchor_nodes
    }

    path_lengths = []

    anchor_node: str
    shortest_path_lookup: Dict[str, int]
    for anchor_node, shortest_path_lookup in nodes_shortest_path_lookup.items():
        if anchor_node in motif:
            path_lengths.append(0)
            continue
        shortest_path = min([shortest_path_lookup.get(n, -1) for n in motif])

        path_lengths.append(shortest_path)
    return path_lengths


def motif_module_participation(g: nx.Graph, modules: List[List[str]], motif: List[str]):
    participations = []
    for i, p in enumerate(modules):
        for node in motif:
            if node in p:
                participations.append(i)
                break
    return participations


def process_motifs(
        g: nx.Graph,
        motifs: List[List[str]],
        anchor_nodes_generator: Callable[[nx.Graph], List[str]] = get_hubs,
        graph_modules_generator: Callable[[nx.Graph], List[List[str]]] = get_modularity_communities,
        disable_tqdm: bool = False):
    """Calculate motif positional metrics"""
    anchor_nodes = anchor_nodes_generator(g)
    graph_modules = graph_modules_generator(g)

    pbar_hub_distance = tqdm(motifs, desc="Calculating hub distances", leave=False, disable=disable_tqdm)
    hub_distance = [motif_distance_to_nodes(g, anchor_nodes, motif) for motif in pbar_hub_distance]

    pbar_partition_participation = tqdm(
        motifs, desc="Calculating modularity partitions", leave=False, disable=disable_tqdm,
    )
    partition_participation = [
        motif_module_participation(g, graph_modules, motif)
        for motif in
        pbar_partition_participation
    ]

    pbar_degree = tqdm(motifs, desc="Calculating motif degrees", leave=False, disable=disable_tqdm)
    motif_degree = [get_group_degree(g, motif) for motif in pbar_degree]

    positional_metrics = {}
    for i, motif in enumerate(tqdm(motifs, desc="Packing motif data", leave=False, disable=disable_tqdm)):
        positional_metrics[i] = {
            "motif_degree": motif_degree[i],
            "hub_distances": hub_distance[i],
            "partition_participation": partition_participation[i],
        }

    return {
        "anchor_nodes": anchor_nodes,
        "graph_modules": graph_modules,
        "positional_metrics": positional_metrics,
    }


def calculate_metrics(
        motif_graph: MotifGraph,
        motif_size: int,
        anchor_nodes_generator: Callable[[nx.Graph], List[str]] = get_hubs,
        graph_modules_generator: Callable[[nx.Graph], List[List[str]]] = get_modularity_communities,
        disable_tqdm: bool = False):
    """When pointed to a graph and a motif file, unzips the motif file, reads the graph and calculates various
    positional metrics"""
    g = nx.readwrite.edgelist.read_edgelist(motif_graph.get_graph_path(), data=False, create_using=nx.Graph)
    motifs = [motif_data["nodes"] for motif_index, motif_data in motif_graph.load_motif_pos_zip(motif_size).items()]

    return process_motifs(g, motifs, anchor_nodes_generator, graph_modules_generator, disable_tqdm)
