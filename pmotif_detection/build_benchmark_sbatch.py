from pathlib import Path

LOG_BASE = "/hpi/fs00/home/tim.garrels/masterthesis/logs/benchmarking_logs/"

datasets = [
    "kaggle_so_tags.edgelist",
    "kaggle_star_wars.edgelist",
    "yeastInter_st.txt",
    "random_graphs/0_barabasi_albert_graph_m_1",
    "random_graphs/0_barabasi_albert_graph_m_2"
    "random_graphs/0_ferdos_renyi_graph_m_2000",
    "human_cancer_cutoff_0.935.edgelist",
    "human_brain_development_cutoff_0.772.edgelist",
]

graphlet_sizes = [3, 4]
benchmarking_runs = [1, 2, 3, 4, 5]


def generate_line(edgelist_path: Path, graphlet_size: int, benchmarking_run: int):
    log_path = LOG_BASE + str(graphlet_size) + "/" + edgelist_path.name
    return f"./run_benchmark.sh {log_path} {str(edgelist_path)} {graphlet_size} {benchmarking_run}"


total_jobs = len(datasets) * len(graphlet_sizes) * len(benchmarking_runs)

preamble_lines = [
    "#!/bin/bash",
    "#SBATCH -A renard",
    "#SBATCH --time=40:00:00",
    "#SBATCH --cpus-per-task=8",
    "#SBATCH --mem-per-cpu=150G",
]


with open(f"slurm_benchmark.batch", "w") as f:
    for l in preamble_lines:
        f.write(l)
        f.write("\n")

    f.write("\n")

    for graphlet_size in graphlet_sizes:
        for d in datasets:
            for benchmarking_run in benchmarking_runs:

                f.write(generate_line(Path(d), graphlet_size, benchmarking_run))
                f.write("\n")
