"""This utility takes a network and nodes (or supernodes)
and calculates various positional metrics for those inputs"""
import statistics
from pathlib import Path
from typing import List
from tqdm import tqdm
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from motif_position_tooling.utils.motif_io import load_motif_zip
from motif_position_tooling.utils.motif_io import MotifGraph

WORKERS = 8


def get_hubs(g: nx.Graph):
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


def get_group_betweenness(g: nx.Graph, motifs: List[List[int]]):
    return nx.group_betweenness_centrality(g, motifs)


def distance_to_hubs(g: nx.Graph, hubs: List[str], motif: List[str]):

    hubs_shortest_path_lookup = {i: nx.single_source_shortest_path_length(g, h) for i, h in enumerate(hubs)}

    path_lengths = []
    for i, shortest_path_lookup in hubs_shortest_path_lookup.items():
        if hubs[i] in motif:
            path_lengths.append(0)
            continue
        shortest_path = min([shortest_path_lookup.get(n, -1) for n in motif])

        path_lengths.append(shortest_path)
    return path_lengths


def modularity_communities(g: nx.Graph):
    return list(map(list, greedy_modularity_communities(g)))


def find_partition_participation(g: nx.Graph, partitions, motif: List[str]):
    participations = []
    for i, p in enumerate(partitions):
        for node in motif:
            if node in p:
                participations.append(i)
                break
    return participations


def get_motif_degree(g: nx.Graph, motif: List[str]):
    nodes = set(motif)
    all_edges = g.edges(motif)
    external_degree = 0
    for (u, v) in all_edges:
        if u in nodes and v in nodes:
            # Edge within motif
            continue
        external_degree += 1
    return external_degree


def calculate_metrics(motif_graph: MotifGraph, motif_size: int):
    """When pointed to a graph and a motif file, unzips the motif file, reads the graph and calculates various
    positional metrics"""
    g = nx.readwrite.edgelist.read_edgelist(motif_graph.get_graph_path())
    motifs = load_motif_zip(motif_graph.get_motif_pos_zip(motif_size))

    return process_motifs(g, motifs)


def process_motifs(g: nx.Graph, motifs: List[List[str]]):
    """Calculate motif positional metrics"""
    hubs = get_hubs(g)
    modularity_partitions = modularity_communities(g)

    data = {"hubs": hubs, "modularity_partitions": modularity_partitions, "motif_data": {}}

    pbar_hub_distance = tqdm(motifs, desc="Calculating hub distances", leave=False)
    hub_distance = [distance_to_hubs(g, data["hubs"], motif) for motif in pbar_hub_distance]

    pbar_partition_participation = tqdm(motifs, desc="Calculating modularity partitions", leave=False)
    partition_participation = [
        find_partition_participation(g, data["modularity_partitions"], motif)
        for motif in
        pbar_partition_participation
    ]

    pbar_degree = tqdm(motifs, desc="Calculating motif degrees", leave=False)
    motif_degree = [get_motif_degree(g, motif) for motif in pbar_degree]

    for i, motif in enumerate(tqdm(motifs, desc="Packing motif data", leave=False)):
        data["motif_data"][i] = (i, {
            "motif_degree": motif_degree[i],
            "hub_distances": hub_distance[i],
            "partition_participation": partition_participation[i],
        })
    return data
