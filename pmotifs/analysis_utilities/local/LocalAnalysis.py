from enum import Enum
from typing import List

import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import mannwhitneyu
from statistics import quantiles

from pmotifs.analysis_utilities.analysis_result_collector import result_df_filtered_by_graphlet_class
from pmotifs.analysis_utilities.loading import Result
from pmotifs.graphlet_representation import graphlet_classes_from_size, graphlet_class_to_name


class QuantileFilter(Enum):
    below_1p = 0
    below_5p = 4
    above_1p = -1
    above_5p = -5


class LocalAnalysis:
    """Analysis based on the original graph alone (no random graphs)"""
    def __init__(self, r: Result):
        self._result = r
        self._graphlet_classes = graphlet_classes_from_size(r.graphlet_size)

        self.graphlet_class_histogram = None
        self.hist_per_class = None
        self.hist_per_class_with_percentiles = None
        self.mann_whitney_u_results = None

    def _plot_graphlet_class_histogram(self, p_metric: str, graphlet_class: str):
        fig, ax = plt.subplots(1, 1)
        result_df_filtered_by_graphlet_class(self._result, graphlet_class)[p_metric].plot.hist(
            ax=ax,
            label=p_metric,
        )
        ax.set_title(graphlet_class_to_name(graphlet_class))
        ax.legend()
        return fig, ax

    def _plot_percentile_lines(self, ax, p_metric: str, graphlet_class: str):
        metric = result_df_filtered_by_graphlet_class(self._result, graphlet_class)[p_metric]

        percentile_cuts = quantiles(metric, n=100, method="inclusive")
        ax.hist(metric, label=graphlet_class_to_name(graphlet_class))
        ax.axvline(percentile_cuts[0], label=f"<1% ({round(percentile_cuts[0], 2)})", color="orange", alpha=0.5)
        ax.axvline(percentile_cuts[4], label=f"<5% ({round(percentile_cuts[4], 2)})", color="green", alpha=0.5)
        ax.axvline(percentile_cuts[-1], label=f">99% ({round(percentile_cuts[-1], 2)})", color="orange", alpha=0.5)
        ax.axvline(percentile_cuts[-5], label=f">95% ({round(percentile_cuts[-5], 2)})", color="green", alpha=0.5)

        ax.legend()
        ax.set_xlabel(p_metric)
        ax.set_ylabel("Frequency")
        ax.set_title(graphlet_class_to_name(graphlet_class))

    def graphlet_class_analysis(self, p_metric: str):
        """Local Scope 1 - Analyses the different graphlet classes within a graph in regard to the given p metric
        Returns a dictionary with the analysis results (data and figures)"""

        # Create Hist per class
        self.hist_per_class = {}
        for graphlet_class in self._graphlet_classes:
            fig, ax = self._plot_graphlet_class_histogram(p_metric, graphlet_class)
            self.hist_per_class[graphlet_class] = fig

        # Combined hist
        self.graphlet_class_histogram, ax = plt.subplots(1, 1)
        x = [
            result_df_filtered_by_graphlet_class(self._result, graphlet_class)[p_metric]
            for graphlet_class in self._graphlet_classes
        ]
        ax.hist(x, label=[graphlet_class_to_name(graphlet_class) for graphlet_class in self._graphlet_classes])
        ax.legend()
        ax.set_xlabel(p_metric)
        ax.set_ylabel("Frequency")
        ax.set_title(
            f"{p_metric}\nHistogram of all {self._result.graphlet_size}-Graphlets"
        )

        # Dump mann_whitney_u test result table
        self.mann_whitney_u_results = pd.DataFrame(
            index=self._graphlet_classes,
            columns=self._graphlet_classes,
        )

        for graphlet_class_x in self._graphlet_classes:
            x = result_df_filtered_by_graphlet_class(self._result, graphlet_class_x)[p_metric]
            for graphlet_class_y in self._graphlet_classes:
                y = result_df_filtered_by_graphlet_class(self._result, graphlet_class_y)[p_metric]
                stat = mannwhitneyu(x, y)
                self.mann_whitney_u_results[graphlet_class_x][graphlet_class_y] = {
                    "statistic": stat.statistic,
                    "pvalue": stat.pvalue,
                }

        rename_lookup = {
            graphlet_class: graphlet_class_to_name(graphlet_class)
            for graphlet_class in self._graphlet_classes
        }
        self.mann_whitney_u_results.rename(
            index=rename_lookup,
            columns=rename_lookup,
            inplace=True,
        )
        self.mann_whitney_u_results.style.set_caption("Mann-Whitney-U-test")

    def graphlet_occurrence_analysis(self, p_metric: str):
        self.hist_per_class_with_percentiles = {}
        for graphlet_class in self._graphlet_classes:
            fig, ax = self._plot_graphlet_class_histogram(p_metric, graphlet_class)
            self._plot_percentile_lines(ax, p_metric, graphlet_class)
            self.hist_per_class_with_percentiles[graphlet_class] = fig

    def get_graphlet_occurrences(self, p_metric: str, graphlet_class: str, quantile_filter: QuantileFilter):
        metric = result_df_filtered_by_graphlet_class(self._result, graphlet_class)[p_metric]
        percentile_cuts = quantiles(metric, n=100, method="inclusive")

        if quantile_filter.value >= 0:
            # We index the filter element from the start, so we want to find values below, comparator is <
            comparator = lambda a, b: a < b
        else:
            # We index the filter element from the end, so we want to find values above, comparator is >
            comparator = lambda a, b: a > b

        quantile_filter_callback = lambda e: comparator(e, percentile_cuts[quantile_filter.value])
        kept_positions = [quantile_filter_callback(e) for e in metric]
        return list(result_df_filtered_by_graphlet_class(self._result, graphlet_class)[kept_positions]["nodes"])

    def single_graphlet_occurrence(self, p_metric: str, graphlet_occurrence: List[str]):
        chosen_occurrence = self._result.positional_metric_df[
            self._result.positional_metric_df["nodes"].isin([graphlet_occurrence])
        ]
        if len(chosen_occurrence) != 1:
            raise ValueError(f"No such occurrence ({graphlet_occurrence})!")




