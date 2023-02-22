"""This file tries to generate a scale free graph using networkx which is a directed multigraph as per implementation
It is then converted to an undirected simple graph, and checked whether the graph is still scale free
"""
import networkx as nx
import powerlaw
import matplotlib.pyplot as plt


def test():
    g = nx.scale_free_graph(100000)
    original_degree_sequence = list(sorted([d for _, d in g.degree], reverse=True))
    original_fit = powerlaw.Fit(original_degree_sequence, xmin=1)

    g: nx.Graph = nx.Graph(g)
    degree_sequence = list(sorted([d for _, d in g.degree], reverse=True))
    fit = powerlaw.Fit(degree_sequence, xmin=1)

    fig, axes = plt.subplots(1,2)
    original_fit.plot_pdf(ax=axes[0])
    original_fit.power_law.plot_pdf(ax=axes[0])
    axes[0].set_title("Original")

    fit.plot_pdf(ax=axes[1])
    fit.power_law.plot_pdf(ax=axes[1])
    axes[1].set_title("Undirected")

    fig.show()


test()
