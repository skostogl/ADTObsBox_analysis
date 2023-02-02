import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from useful_tools.useful_functions import *

path = "ADTObsBox_data_from2022"
filenames_to_consider = [f"{path}/{i}" for i in os.listdir(path) if i.endswith("h5")]

print(filenames_to_consider)


adt = ADT(filenames_to_consider)
myDict = adt.importEmptyDF

fourier_tot_real, fourier_tot_imag, fourier_tot_real_corr, fourier_tot_imag_corr, bunch_number_tot, time_tot, pu_tot, beam_plane_tot = [], [], [], [], [], [], [], []

repeat_fft = 3
frev = 11245.5
which_bunch_b1 = 'all'
which_bunch_b2 = 'all'

for beamplane in myDict.keys():
    print(beamplane, beamplane[0:2])
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
                if which_bunch_b1 =='all':
                   idx = np.where(abs(data[0,:])>0.0)[0]
                else:
                    idx = which_bunch_b1

            elif beamplane[0:2] == 'B2':
                if which_bunch_b2 =='all':
                   idx = np.where(abs(data[0,:])>0.0)[0]
                else:
                    idx = which_bunch_b2
            
            print(f"Bunch slots {idx}")
            for idd in idx:
              #try:
              if True:

    
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
              #except:
              #  print('prob') 
    #except:
    #    print('prob, load_data')

dff = pd.DataFrame({'fourier_corr_real': fourier_tot_real_corr, "fourier_corr_imag": fourier_tot_imag_corr,'fourier_real': fourier_tot_real, 'fourier_imag': fourier_tot_imag,  'bunch': bunch_number_tot, 'time': time_tot, 'beam-plane': beam_plane_tot, 'pu': pu_tot})


for key, group in dff.groupby("time"):
    aux = group.apply(lambda x: x.fourier_corr_real + 1j*x.fourier_corr_imag, axis=1).mean()
    
    freqs = np.linspace(0, 11245.5*repeat_fft, len(aux))
    fig, ax = plt.subplots()
    plt.semilogy(freqs, abs(aux)) 
    plt.xlabel("f (Hz)")
    plt.ylabel(r"FFT ($\rm \mu m$)")
    plt.title(key)
    plt.ylim(0,5.0)
    plt.xlim(0, frev*repeat_fft*0.5)
    plt.show()
    
