# %%
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
from pathlib import Path

config=yaml.safe_load(open('config.yaml'))

fillnb = 8470
study_name = f"Fill{fillnb}"
save_to = "/eos/user/s/skostogl/analysis_test"

Path(save_to).mkdir(parents=True, exist_ok=True)

mypython = "/afs/cern.ch/work/s/skostogl/private/workspaces/HLLHC_xsuite_Jul22/example_DA_study/miniconda/bin/activate"


filenames = pd.read_parquet(f"filenames_{study_name}.parquet").filenames.values
n = 2
filenames_in_chunks = [filenames[i * n:(i + 1) * n] for i in range((len(filenames) + n - 1) // n )]

bunch_nb_b1 = ['all']
bunch_nb_b2 = ['all']

make_path = 'ADTObsBox_data'
mysymbolic_link = f"sshfs skostogl@lxplus.cern.ch:/eos/project/l/lhc-lumimod/MD7003/ADTObsBox/data_Fill8470 {make_path} -o IdentityFile=/afs/cern.ch/user/s/skostogl/.ssh/id_rsa"

children={}
for child in range(len(filenames_in_chunks)):
    children[f"{study_name}/{child:03}"] = {
                                    'adt_file':filenames_in_chunks[child].tolist(),
                                    'save_to': f"{save_to}/results_fft_{fillnb}_{child:03}.parquet",
                                    'bunch_nb_b1':bunch_nb_b1,
                                    'bunch_nb_b2':bunch_nb_b2,
                                    'log_file': f"{os.getcwd()}/{study_name}/{child:03}/tree_maker.log"
                                    }

config['root']['children'] = children
config['root']['setup_env_script'] = mypython
config['root']['symbolic_link'] = mysymbolic_link
config['root']['make_path'] = make_path

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
