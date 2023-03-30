#sh
#ssh lxplus
#ssh-keygen
#ssh-copy-id sterbini@cs-ccr-dev1
# then you should be able to ssh  sterbini@cs-ccr-dev1 w/o password
#mkdir test
#sshfs sterbini@cs-ccr-dev1:/nfs temp -o IdentityFile=/afs/cern.ch/user/s/sterbini/.ssh/id_rsa
import numpy as np
import glob
import pandas as pd
from pathlib import Path
import subprocess
import datetime

# Path that files will me mounted
path = 'ADTObsBox_data'

# Simplify the search of files
#day  = "*" # in CET
day  = "30" # in CET
##time = "*" 
time = "*" 
#beamplane = "*"#"*"
beamplane = "B1H"#"*"
pu        = "Q7"#"*"

# Subsample 
sample_files = False
if sample_files:
  sample_freq = 60 #in sec

# Fill nb
fill_nb = 8508

save_to = f"filenames_Fill{fill_nb}.parquet" 

# If true, will search in fill.parquet for t1-t2. otherwise, user can define t1-t2 manually
read_fill_info = True

mysymbolic_link = f"sshfs skostogl@cs-ccr-dev1.cern.ch:/nfs/cfc-sr4-adtobs2buf/obsbox/slow {path} -o IdentityFile=/afs/cern.ch/user/s/skostogl/.ssh/id_rsa"
file_format = f"{path}/{beamplane}_{pu}/{day}/{time}/*"
#mysymbolic_link = f"sshfs skostogl@lxplus.cern.ch:/eos/project/l/lhc-lumimod/MD7003/ADTObsBox/data_Fill8470 {path} -o IdentityFile=/afs/cern.ch/user/s/skostogl/.ssh/id_rsa"
#mysymbolic_link = f"sshfs skostogl@lxplus.cern.ch:/eos/project/l/lhc-lumimod/MD7003/ADTObsBox/data_Fill8469_copy {path} -o IdentityFile=/afs/cern.ch/user/s/skostogl/.ssh/id_rsa"
#file_format = f"{path}/{beamplane}_{pu}*"

if read_fill_info:
  df_modes = pd.read_parquet("fills.parquet")
  #print(df_modes)  
  df_fills = pd.read_parquet("fills.parquet")
  if df_fills['HX:FILLN'].iloc[0] == None:
    df_fills['HX:FILLN'].iloc[0] = df_fills['HX:FILLN'].dropna().iloc[0]
  df_fills['HX:FILLN'] = df_fills['HX:FILLN'].ffill(axis=0)
  
  df_current = df_fills[df_fills['HX:FILLN'] == str(fill_nb)]
  
  t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'INJPHYS'].index[0], tz='UTC')
  try:
    t2 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'BEAMDUMP'].index[0], tz='UTC')
  except:
    print("BEAMDUMP not found!")
    t2 = pd.Timestamp(df_current.index[-1], tz='UTC')
  print(t1,t2)
else:
  t1 = pd.Timestamp('2022-11-05 20:10', tz='UTC')
  t2 = pd.Timestamp('2022-11-05 20:50', tz='UTC')

print(f"Time range considered (UTC): {t1}-{t2}")

def fromName2Timestamp(current_fileName,tz_start='CET',tz_end='UTC'):
        year = current_fileName.split('_')[-2][0:4]
        month = current_fileName.split('_')[-2][4:6]
        day   = current_fileName.split('_')[-2][6:]
        full_datetime = f'{day}/{month}/{year} ' + current_fileName.split('_')[-1].split('.')[0]
        return pd.Timestamp(datetime.datetime.strptime(full_datetime,"%d/%m/%Y %Hh%Mm%Ss%fus")).tz_localize(tz_start, ambiguous=False).tz_convert(tz_end)

def find_pickup(current_fileName):
	return current_fileName.split('_')[-3]

def find_beamplane(current_fileName):
	return current_fileName.split('_')[-4].split("/")[-1]


# Create symbolic link
Path(path).mkdir(parents=True, exist_ok=True)
subprocess.call(f"fusermount -u {path}", shell=True)
print("Mounting NFS..")
subprocess.call(f"{mysymbolic_link}", shell=True)


print("Looking for files..")
filenames = (glob.glob(file_format))
filenames.sort(key = lambda x: fromName2Timestamp(x.split("/")[-1]))

# Filter based on time
t1 = t1.tz_convert("CET")
t2 = t2.tz_convert("CET")
print(f"Selected files from {t1} to {t2} CET")
print("")
filenames_to_consider = np.array([i for i in filenames if (fromName2Timestamp(i.split("/")[-1])>=t1) and (fromName2Timestamp(i.split("/")[-1])<=t2)])
print(f"Found {len(filenames_to_consider)} files fitting criteria")

# This is needed to sample the h5 files, first group them in pu and beamplanes and then select sampling files with a timestamps sampled at 1 minute
if sample_files:
  print("Sampling files..")
  sampled_filenames_to_consider = []

  pus_to_consider = [find_pickup(i) for i in filenames_to_consider]
  beamplane_to_consider = [find_beamplane(i) for i in filenames_to_consider]
  
  for current_pu in np.unique(pus_to_consider):
  	for current_beamplane in np.unique(beamplane_to_consider):
  		print(current_pu, current_beamplane)
  		current_filenames = np.array([i for i in filenames_to_consider if current_pu in i and current_beamplane in i])
  		#print(current_filenames)
  		if len(current_filenames)>0:
                
  			times  = [fromName2Timestamp(x.split("/")[-1]) for x in current_filenames]
  			sampled_times = pd.date_range(times[0], times[-1], freq=f"{sample_freq}S")
  			closest_idxs = np.array([ min(enumerate(times), key=lambda b: abs(time-b[1]))[0] for time in sampled_times])
  			filenames_to_consider_temp = current_filenames[closest_idxs]
  			sampled_filenames_to_consider.append(filenames_to_consider_temp)
  
  filenames_to_consider = np.array(sampled_filenames_to_consider).flatten()
  print(f"Found {len(filenames_to_consider)} files after subsampling")

pd.DataFrame({"filenames": filenames_to_consider}).to_parquet(save_to)

#print(pd.DataFrame({"filenames": filenames_to_consider}))

# Unmount
#subprocess.call(f"fusermount -u {path}", shell=True)
