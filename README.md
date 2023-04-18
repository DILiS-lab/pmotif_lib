# pmotif-lib

Perform motif detection, either with traditional frequency, or with positional metrics for each graphlet occurrence.

This library implements each step of a (p)motif detection pipeline such as 
- graphlet detection in networks
- randomization of networks
- frequency comparison of graphlet occurrences
- positional metric comparison of graphlet occurrences.

## Setup
Install this package:
```
pip install pmotif-lib
```

This library relies on the `gtrieScanner` tool. Please [download it](https://www.dcc.fc.up.pt/gtries/) and compile it.

## Usage
See `showcase/` for a number of examples:
- graphlet detection
- p-graphlet detection
- motif detection
- p-motif detection

## Glossary
- Induced Subgraph: A graph created by cutting out a set of nodes from a graph `G`, retaining all edges between these nodes
- Isomorphic graphs: Graphs, that are structurally the same when ignoring node labels
- Isomorphic Classes of Size k: A set of graphs with k nodes, so that every other graph with k nodes is isomorphic to one graph in the set
- k-Graphlet: An isomorphic class of size k, so that at least one induced subgraph in a graph `G` is isomorphic to that class
- Graphlet Occurrences: All induced sub-graphs in a graph `G` that belong to a specific k-Graphlet
- Graphlet Frequency: The number of graphlet occurrences of a specific k-graphlet in a graph `G`
- Graph Motif: A k-Graphlet, which has a graphlet frequency which is significantly higher than expected, usually tested against randomized graphs generated based on `G`
- p-Motif: A k-Graphlet, which has graphlet occurrences with a significant expression of a positional metric, when compared against randomized graphs generated based on `G`
