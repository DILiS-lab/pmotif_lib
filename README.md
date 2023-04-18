# pmotif_lib

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

This library relies on the `gtrieScanner` tool. Please [download it](https://www.dcc.fc.up.pt/gtries/), compile it, and add the executable to your path.

Finally, this library loads environment variables. Create an `.env` file::
```bash
export DATASET_DIRECTORY=/path/where/edgelists/are/located
export EXPERIMENT_OUT=/path/where/raw/graphlets/and/pmetric/should/go
export GTRIESCANNER_EXECUTABLE=/path/to/the/gtriescanner/executable
export WORKERS=1  # Optional, controls the max. degree of parallelization
```
In order to make these variablea available to the library, use `source .env` before command line usage!
You can also use the `python-dotenv` package to load the `.env` file from python code:
```python
from dotenv import load_dotenv

load_dotenv(".env")
```

## Usage
`showcase/` contains a number of examples:
- graphlet detection
- p-graphlet detection
- motif detection
- p-motif detection

After installing `pmotif_lib`, navigate into `showcase/`, run `source .showcase_env`, and then run `python3 graphlet_detection` (or one of the other examples).
This expects the `gtrieScanner` executable to be in your system's path under `gtrieScanner`!

## Glossary
- Induced Subgraph: A graph created by cutting out a set of nodes from a graph `G`, retaining all edges between these nodes
- Isomorphic graphs: Graphs, that are structurally the same when ignoring node labels
- Isomorphic Classes of Size k: A set of graphs with k nodes, so that every other graph with k nodes is isomorphic to one graph in the set
- k-Graphlet: An isomorphic class of size k, so that at least one induced subgraph in a graph `G` is isomorphic to that class
- Graphlet Occurrences: All induced sub-graphs in a graph `G` that belong to a specific k-Graphlet
- Graphlet Frequency: The number of graphlet occurrences of a specific k-graphlet in a graph `G`
- Graph Motif: A k-Graphlet, which has a graphlet frequency which is significantly higher than expected, usually tested against randomized graphs generated based on `G`
- p-Motif: A k-Graphlet, which has graphlet occurrences with a significant expression of a positional metric, when compared against randomized graphs generated based on `G`
