
import pandas as pd
import tree_maker
from tree_maker import NodeJob
from tree_maker import initialize
import time
import os
from pathlib import Path
import itertools
import numpy as np
import yaml
from user_defined_functions import generate_run_sh
from user_defined_functions import generate_run_sh_htc

# Import the configuration
config=yaml.safe_load(open('config.yaml'))

fills_path  = "/afs/cern.ch/work/s/skostogl/private/adt_nxcals/fills.parquet"

fill_nb_s   = pd.read_parquet(fills_path)["HX:FILLN"].dropna().unique()

chunks_per_job = 1 # number of scan points in each job

all_jobs = itertools.product(fill_nb_s)
all_jobs = np.array([i for i in all_jobs])
all_jobs_split =np.array([all_jobs[i:i + chunks_per_job, :] for i in range(0, len(all_jobs), chunks_per_job)])

study_name        = "ADT_2022_2"
save_plots_to_eos = "/eos/user/s/skostogl/ADTObsBox_2022_nxcals"
mypython          = "/afs/cern.ch/work/s/skostogl/private/workspaces/HLLHC_xsuite_Jul22/example_DA_study/miniconda/bin/activate"

children={}
for child in range(len(all_jobs_split)):
    children[f"{study_name}/{child:03}"] = {
                                    'fill_nb':all_jobs_split[child].T[0].tolist(),
                                    'fills_path': fills_path,
                                    'save_to': save_plots_to_eos,
                                    'log_file': f"{os.getcwd()}/{study_name}/{child:03}/tree_maker.log"
                                    }

if config['root']['use_yaml_children']== False:
    config['root']['children'] = children
config['root']['setup_env_script'] = mypython

# Create tree object
start_time = time.time()
root = initialize(config)
print('Done with the tree creation.')
print("--- %s seconds ---" % (time.time() - start_time))

# From python objects we move the nodes to the file-system.
start_time = time.time()
#root.make_folders(generate_run_sh)
root.make_folders(generate_run_sh_htc)
print('The tree folders are ready.')
print("--- %s seconds ---" % (time.time() - start_time))

import shutil
shutil.move("tree_maker.json", f"tree_maker_{study_name}.json")
shutil.move("tree_maker.log", f"tree_maker_{study_name}.log")
