from pathlib import Path

LOG_BASE = "/hpi/fs00/home/tim.garrels/masterthesis/logs/data_collection/"

datasets = [
    # "com-dblp.ungraph.txt",
    "kaggle_so_tags.edgelist",
    "kaggle_star_wars.edgelist",
    # "email-Eu-core.txt",
    # "kaggle_so_tags.node_mapping",
    # "kaggle_star_wars.node_mapping",
    "yeastInter_st.txt",
    "random_graphs/0_barabasi_albert_graph_m_1",
    "random_graphs/0_barabasi_albert_graph_m_2",
    "random_graphs/0_barabasi_albert_graph_m_3",
    "random_graphs/0_ferdos_renyi_graph_m_2000",
    # "random_graphs/0_scale_free_graph_a_28_b_7_g_02",
    # "random_graphs/0_scale_free_graph_a_35_b_3_g_35",
    # "random_graphs/0_scale_free_graph_a_65_b_1_g_25",
    "random_graphs/1_barabasi_albert_graph_m_1",
    "random_graphs/1_barabasi_albert_graph_m_2",
    "random_graphs/1_barabasi_albert_graph_m_3",
    "random_graphs/1_ferdos_renyi_graph_m_2000",
    # "random_graphs/1_scale_free_graph_a_28_b_7_g_02",
    # "random_graphs/1_scale_free_graph_a_35_b_3_g_35",
    # "random_graphs/1_scale_free_graph_a_65_b_1_g_25",
    "random_graphs/2_barabasi_albert_graph_m_1",
    "random_graphs/2_barabasi_albert_graph_m_2",
    "random_graphs/2_barabasi_albert_graph_m_3",
    "random_graphs/2_ferdos_renyi_graph_m_2000",
    # "random_graphs/2_scale_free_graph_a_28_b_7_g_02",
    # "random_graphs/2_scale_free_graph_a_35_b_3_g_35",
    # "random_graphs/2_scale_free_graph_a_65_b_1_g_25",
    "random_graphs/3_barabasi_albert_graph_m_1",
    "random_graphs/3_barabasi_albert_graph_m_2",
    "random_graphs/3_barabasi_albert_graph_m_3",
    "random_graphs/3_ferdos_renyi_graph_m_2000",
    # "random_graphs/3_scale_free_graph_a_28_b_7_g_02",
    # "random_graphs/3_scale_free_graph_a_35_b_3_g_35",
    # "random_graphs/3_scale_free_graph_a_65_b_1_g_25",
    "random_graphs/4_barabasi_albert_graph_m_1",
    "random_graphs/4_barabasi_albert_graph_m_2",
    "random_graphs/4_barabasi_albert_graph_m_3",
    "random_graphs/4_ferdos_renyi_graph_m_2000",
    # "random_graphs/4_scale_free_graph_a_28_b_7_g_02",
    # "random_graphs/4_scale_free_graph_a_35_b_3_g_35",
    # "random_graphs/4_scale_free_graph_a_65_b_1_g_25",
    "human_cancer_cutoff_0.935.edgelist",
    "human_brain_development_cutoff_0.772.edgelist",
]

graphlet_sizes = [3, 4]
random_graphs = 1000


def generate_line(edgelist_path: Path, graphlet_size: int, random_graphs: int):
    log_path = LOG_BASE + str(graphlet_size) + "/" + edgelist_path.name
    return f"./run_data_collection.sh {log_path} {str(edgelist_path)} {graphlet_size} {random_graphs}"


total_jobs = len(datasets) * len(graphlet_sizes)

preamble_lines = [
    "#!/bin/bash",
    "#SBATCH -A renard",
    "#SBATCH --time=40:00:00",
    "#SBATCH --cpus-per-task=8",
    "#SBATCH --mem-per-cpu=150G",
]

random_graphs_for_dataset = {}
for graphlet_size in graphlet_sizes:
    with open(f"slurm_{graphlet_size}.batch", "w") as f:
        for l in preamble_lines:
            f.write(l)
            f.write("\n")

        f.write("\n")

        for d in datasets:
            _random_graphs = random_graphs_for_dataset.get(d, 1000)

            f.write(generate_line(Path(d), graphlet_size, _random_graphs))
            f.write("\n")

            random_graphs_for_dataset[d] = -1
        # f.write("wait\n")
