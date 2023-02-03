import json
import yaml
import time
import pandas as pd
#import tree_maker

import h5py
import numpy as np
import datetime
import pandas as pd

# Modified from https://github.com/sterbini/cl2pd/blob/master/cl2pd/noise.py

class ADT:
    def __init__(self, filenames):
        df = self.extract_file_info(filenames)
        df.sort_index(inplace=True)
        self.importEmptyDF = {bp: df[df['Beam-Plane'] == bp] for bp in np.unique(df['Beam-Plane'])}

    def extract_file_info(self, filenames):
        beam_planes = []
        pus = []
        times = []
        for file_name in filenames:
            bp, pu, date, time = file_name.split('/')[-1].split('_')
            time = self.fromName2Timestamp(f'{bp}_{pu}_{date}_{time}')
            beam_planes.append(bp)
            pus.append(pu)
            times.append(time)
        return pd.DataFrame({'PU': pus, 'Beam-Plane': beam_planes, 'Path': filenames}, index=np.array(times))

    def fromName2Timestamp(self, current_fileName,tz_start='CET',tz_end='UTC'):
        year = current_fileName.split('_')[-2][0:4]
        month = current_fileName.split('_')[-2][4:6]
        day   = current_fileName.split('_')[-2][6:]
        full_datetime = f'{day}/{month}/{year} ' + current_fileName.split('_')[-1].split('.')[0]
        return pd.Timestamp(datetime.datetime.strptime(full_datetime,"%d/%m/%Y %Hh%Mm%Ss%fus")).tz_localize(tz_start, ambiguous=False).tz_convert(tz_end)

    def loadData(self, fileName):
        fi = h5py.File(fileName, 'r')
        beam, plane = fileName.split('_')[-4].split('/')[-1][:2], fileName.split('_')[-4].split('/')[-1][2:3]
        plane = 'horizontal' if plane == 'H' else 'vertical'
        alldat = fi[beam][plane]
        print('Buffer: Turns = %s, Bunches = %s' % (alldat.shape[0], alldat.shape[1]))
        return alldat[:]
    
    def cmp_fft(self, data, specific_bunch, frev=11245.5, first_bunch_slot=0, bunch_spacing=25e-9, repeat_fft=1):
        fourier =  np.fft.fft(data[:,specific_bunch] )
        fourier = fourier/len(fourier)*2.0
        delay   = (specific_bunch-first_bunch_slot)*bunch_spacing
        fourier = np.concatenate([fourier]*repeat_fft)
        freqs   = np.linspace(0, frev*repeat_fft, len(fourier))
        corrected_fourier = fourier*np.exp(-1j*2.0*np.pi*freqs*delay)
        return pd.Series([freqs, fourier.real, fourier.imag, corrected_fourier.real, corrected_fourier.imag])


with open('config.yaml','r') as fid:
    config=yaml.safe_load(fid)

#tree_maker.tag_json.tag_it(config['log_file'], 'started')

filenames_to_consider = config['adt_file']
print(filenames_to_consider)

# Approach with time domain concat for periodic filling scheme
adt = ADT(filenames_to_consider)
myDict = adt.importEmptyDF

repeat_fft = 2
frev = 11245.5
which_bunch_b1 = config["bunch_nb_b1"] #'all'
which_bunch_b2 = config["bunch_nb_b2"]#'all'

df_final = []

for beamplane in myDict.keys():
    print(beamplane)
    myDF = myDict[beamplane].copy()
    #try:
    if True:
      myDF['Data'] = myDF['Path'].apply(adt.loadData)
      
      for counter in range(len(myDF)):
          data = myDF.iloc[counter]['Data']
          time = myDF.iloc[counter].name
          pu   = myDF.iloc[counter].PU
          current_beamplane = myDF.iloc[counter]['Beam-Plane']
          # for each bunch
          if beamplane[0:2] == 'B1':
                if which_bunch_b1 ==['all']:
                   idx = np.where(abs(data[0,:])>0.0)[0]
                else:
                    idx = which_bunch_b1

          elif beamplane[0:2] == 'B2':
                if which_bunch_b2 ==['all']:
                   idx = np.where(abs(data[0,:])>0.0)[0]
                else:
                    idx = which_bunch_b2

          print(f"Bunch slots {idx}")
          fourier_tot_real, fourier_tot_imag, fourier_tot_real_corr, fourier_tot_imag_corr, bunch_number_tot, time_tot, pu_tot, beam_plane_tot = [], [], [], [], [], [], [], []

          for idd in idx[:]:
              try:
                #print(idd)
                #if True:
                #freqs, fourier_real, fourier_imag = adt.cmp_fft(data, specific_bunch=idd)
               
                freqs, fourier_real, fourier_imag, fourier_corr_real, fourier_corr_imag  = adt.cmp_fft(data, specific_bunch=idd, frev=frev, first_bunch_slot=idx[0], bunch_spacing=25e-9, repeat_fft=repeat_fft)
 
                fourier_tot_real.append(fourier_real)
                fourier_tot_imag.append(fourier_imag)
                fourier_tot_real_corr.append(fourier_corr_real)
                fourier_tot_imag_corr.append(fourier_corr_imag)
                
                bunch_number_tot.append(idd)
                time_tot.append(time)
                #freqs_tot.append(freqs)
                pu_tot.append(pu)
                beam_plane_tot.append(current_beamplane) 
              except Exception as e:
                print(f'Error! {e}') 
          dff = pd.DataFrame({'fourier_corr_real': fourier_tot_real_corr, "fourier_corr_imag": fourier_tot_imag_corr,'fourier_real': fourier_tot_real, 'fourier_imag': fourier_tot_imag,  'bunch': bunch_number_tot, 'time': time_tot, 'beam-plane': beam_plane_tot, 'pu': pu_tot})
          aux = abs(dff.apply(lambda x: x.fourier_corr_real + 1j*x.fourier_corr_imag, axis=1).mean())
          df1 = pd.DataFrame({"time":[time], "fourier": [abs(aux)], "pu": [pu], "beam-plane": [current_beamplane], "bunches":[len(idx)]})
          df_final.append(df1)

df2 = pd.concat(df_final, axis=0)
destination = config['save_to']
df2.to_parquet(f"{destination}")

print(df2)
#tree_maker.tag_json.tag_it(config['log_file'], 'completed')
