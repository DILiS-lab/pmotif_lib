from tqdm import tqdm

from pmotif_detection.analyse_scripts.util import add_consolidated_metrics
from pmotifs.analysis_utilities.loading import Result
from pmotifs.config import config
from pmotifs.analysis_utilities.metric_consolidation import metrics

from local_scope import LocalScope
from global_scope import GlobalScope


METRIC_NAMES = metrics.keys()


def execute(graphlet_size: int, dataset: str, experiment_out: str):

    print("Loading result")
    r = Result.load_result(config.DATASET_DIRECTORY / dataset, config.EXPERIMENT_OUT / experiment_out, graphlet_size)
    print("Consolidating metrics")
    r = add_consolidated_metrics(r)

    print("Processing Local Analysis")
    local_scope = LocalScope(r)
    for metric_name in tqdm(METRIC_NAMES, desc="Metric"):
        local_scope.plot_metric_distribution(metric_name)
        local_scope.compute_mann_whitneyu(metric_name)
        local_scope.plot_occurrence_percentiles(metric_name)

    print("Processing Global Analysis")
    global_scope = GlobalScope(r)
    global_scope.plot_graphlet_frequency()
    for metric_name in tqdm(METRIC_NAMES, desc="Metric"):
        global_scope.pmotif_analysis_result(metric_name)
        global_scope.plot_sample_size_distribution(metric_name)
        global_scope.plot_median_distribution(metric_name)


if __name__ == "__main__":
    execute(3, "yeastInter_st.txt", "yeastInter_st")
