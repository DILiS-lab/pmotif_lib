"""Utility script to execute analyses at many abstraction levels with one call
Useful to do exploratory work, as no specific positional metric or scope need to be chosen"""

from pmotifs.analysis_utilities.loading import Result
from pmotifs.analysis_utilities.metric_consolidation import metrics


def analyse(r: Result):
    enrich_with_metrics(r)


def enrich_with_metrics(r: Result):
    """Add all metrics to r dataframe"""
    for metric_name, metric_callback in metrics.items():
        r.positional_metric_df[metric_name] = metric_callback(r)


def result_df_filtered_by_graphlet_class(r: Result, graphlet_class: str):
    return r.positional_metric_df[r.positional_metric_df["graphlet_class"] == graphlet_class]


def local_analysis(r: Result, p_metric: str):

    pass


def global_analysis(r: Result, p_metric: None):
    pass
