"""Configuration constants."""
import os
from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent.parent.parent.parent


DATASET_DIRECTORY = Path(os.getenv("DATASET_DIRECTORY"))
EXPERIMENT_OUT = Path(os.getenv("EXPERIMENT_OUT"))
GTRIESCANNER_EXECUTABLE = Path(os.getenv("GTRIESCANNER_EXECUTABLE"))


WORKERS = 8
