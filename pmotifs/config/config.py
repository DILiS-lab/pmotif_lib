from pathlib import Path

BASE_PATH = Path(__file__).absolute().parent.parent.parent.parent

DATASET_DIRECTORY = BASE_PATH / "datasets"
EXPERIMENT_OUT = BASE_PATH / "output"
GTRIESCANNER_EXECUTABLE = BASE_PATH / "bin" / "gtrieScanner" / "gtrieScanner"

WORKERS = 8
