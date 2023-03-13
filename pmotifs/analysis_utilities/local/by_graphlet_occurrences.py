from typing import Dict

from pmotifs.analysis_utilities.loading import Result
from pmotifs.graphlet_representation import graphlet_classes_from_size


def local_graphlet_class_analysis(r: Result, p_metric: str) -> Dict:
    """Local Scope 2 - Analyses the graphlet occurrences of a graphlet class
    within a graph in regard to the given p metric
    Returns a dictionary with the analysis results (data and figures)"""
    graphlet_classes = graphlet_classes_from_size(r.graphlet_size)
    