import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

fill_nb = 8348
path = f'/eos/project-a/abpdata/lhc/ObsBox/fft_analysis_Fill{fill_nb}'
filenames = os.listdir(path)
filenames = [i for i in filenames if i.endswith('parquet')]
print(filenames)


frev=11245.5

#current_beam = 1
#plane        = "V"
for current_beam in [1, 2]:
  for plane in ["H", "V"]:
    save_to      = "/eos/home-s/skostogl/SWAN_projects/analysis_ADTObsBox/"
    	
    #for pu in ["Q7", "Q8", "Q9", "Q10"]: 
    #for pu in ["Q7", "Q8", "Q9", "Q10"]: 
    for pu in ["Q7"]: 
            beam = current_beam
            for day in [fill_nb]:
                #for beam in [1,2]:
                #prin/eos/project-a/abpdata/lhc/ObsBoxt(day)
                df_tot = {}
    
    
                df_tot[f'B{beam}{plane}'] = []
                #df_tot[f'B{beam}V'] = []
    
                for beam in [current_beam]:
    
    
                    current_filenames = [i for i in filenames if i.startswith(f'fft_{day}')]
                    for current_filename in current_filenames[:]:
                        print(f'{path}/{current_filename}')
                        df = pd.read_parquet(f'{path}/{current_filename}')
                        df = df[df["pu"] == pu]
                        
                        for beam_plane in [f'B{beam}{plane}']:
                        #for beam_plane in [f'B{beam}H']:
                                
                                df2 = df[ df['beam-plane'] == beam_plane].copy()
                                #print(df2)
                                if not df2.empty:
                                    #print(df2, beam_plane)
                                    #df2['fourier_abs'] = (df2.apply(lambda x: abs(x['fourier_real'] + 1j*x['fourier_imag']), axis=1))
                                    #df2["freqs"] = df2.apply(lambda x: np.linspace(0, len(x.bunches)*frev, len(x["fourier_abs"])), axis=1)
                                    #df2["num_bunches"] = df2.apply(lambda x: len(x.bunches), axis=1)
                                    dff = df2[['fourier', 'time', 'pu', 'bunches']]
                                    df_tot[beam_plane].append(dff)
                                else:
                                    print("no pu data found")
    
    
    
                for beam_plane in [f'B{beam}{plane}' ]: 
                        df_tot2 = pd.concat(df_tot[beam_plane], axis=0)
                        df_tot2.sort_values(by='time', inplace=True)
                        for i in np.diff(df_tot2.time):
                            print(i)
    
                        df_tot2.to_parquet(f'{save_to}/FFT_Fill{day}_{pu}_{beam_plane}.parquet')
