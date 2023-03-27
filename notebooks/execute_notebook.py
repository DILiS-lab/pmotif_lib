import os
from pathlib import Path

from pmotifs.analysis_utilities.metric_consolidation import metrics

OUTPUT = Path("/home/timgarrels/Projects/masterthesis/motif_position_tooling/notebook_reports")
os.makedirs(OUTPUT, exist_ok=True)

NOTEBOOK_BASE = "/home/timgarrels/Projects/masterthesis/motif_position_tooling/notebooks/"
NOTEBOOKS = [
    NOTEBOOK_BASE + 'Interfaces/Local Scope 1 - Is a graphlet class more prevalent than others?.ipynb',
    NOTEBOOK_BASE + 'Interfaces/Local Scope 2 - Which graphlet occurrence more prevalent than others?.ipynb',
    # 'Local Scope 3 - Is a graphlet occurrence more prevalent than others?.ipynb',
    # 'Local Scope 4 - Which structures are based on this node?.ipynb',
    NOTEBOOK_BASE + 'Interfaces/Global Scope 1 - Is a graphlet class a motif?.ipynb',
    NOTEBOOK_BASE + 'Interfaces/Global Scope 2 - Is a graphlet class a positional motif?.ipynb',
    # 'Global Scope 3 - Is a graphlet occurrence a positional motif?.ipynb',
]

METRICS = metrics.keys()

# Analysis Parameters
graphlet_size = 3
dataset = "yeastInter_st.txt"
experiment_out = "yeastInter_st"


for notebook in NOTEBOOKS:
    notebook_abbr = Path(notebook).stem.split(" -")[0].replace(" ", "_")
    print("Converting", notebook_abbr)
    # Escape notebook names which contain spaces
    notebook = notebook.replace(" ", r"\ ")
    for metric_name in metrics:
        metric_abbr = metric_name.replace(" ", "_")
        print("\tMetric:", metric_abbr)
        output_dir = OUTPUT / experiment_out / str(graphlet_size)
        os.makedirs(output_dir, exist_ok=True)

        output = output_dir / (notebook_abbr + "_" + metric_abbr)

        env_var_string = f"GRAPHLET_SIZE={graphlet_size} DATASET='{dataset}' EXPERIMENT_OUT='{experiment_out}' METRIC_NAME='{metric_name}'"
        nbconvert_command = f"jupyter nbconvert --log-level WARN --execute --to html --template full --output '{output}' {notebook}"

        os.system(env_var_string + " " + nbconvert_command)
