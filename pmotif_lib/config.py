"""Configuration constants."""
from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent.parent.parent.parent

DATASET_DIRECTORY = BASE_PATH / "datasets"
EXPERIMENT_OUT = BASE_PATH / "output" / "data_collection_out"
ANALYSIS_OUT = BASE_PATH / "output" / "analysis_out"
GTRIESCANNER_EXECUTABLE = BASE_PATH / "bin" / "gtrieScanner" / "gtrieScanner"

WORKERS = 8
