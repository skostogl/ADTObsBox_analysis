import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates

import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage.filters import gaussian_filter
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.patches as mpatches
params = {'xtick.labelsize': 20,
'ytick.labelsize': 20,
'font.size': 20,
'figure.autolayout': True,
'figure.figsize': (12, 9),
'axes.titlesize' : 23,
'axes.labelsize' : 23,
'lines.linewidth' : 1,
'lines.markersize' : 6,
'legend.fontsize': 18,
'mathtext.fontset': 'stix',
'font.family': 'STIXGeneral'}
#plt.rcParams['figure.dpi'] = 300
plt.rcParams.update(params)
#plt.rcParams.update(plt.rcParamsDefault)


#filename = "FFT_6Jul_Q10_B1H.parquet"
#filename = "FFT_6Jul_sampled1min_Q10_B1H.parquet"
path = "/eos/home-s/skostogl/SWAN_projects/analysis_ADTObsBox"

fill_nb = 7966
for filename in [f"FFT_Fill{fill_nb}_Q10_B1H.parquet",
                 f"FFT_Fill{fill_nb}_Q10_B1V.parquet",
                 f"FFT_Fill{fill_nb}_Q10_B2H.parquet",
                 f"FFT_Fill{fill_nb}_Q10_B2V.parquet"]:

  #filename = "FFT_Fill7966_Q10_B2V.parquet"
  pu = filename.split("_")[-2]
  fill = filename.split("_")[1][4:]
  print(fill)
  beamplane = filename.split("_")[-1].split(".")[0]
  
  df = pd.read_parquet(f"{path}/{filename}")
  df.set_index("time", inplace=True)
  save_to  = f"{path}/plots_{fill}_{beamplane}_{pu}"
  from pathlib import Path
  Path(save_to).mkdir(parents=True, exist_ok=True)
  
  my_df = pd.read_parquet(f'/eos/project/l/lhc-lumimod/LuminosityFollowUp/2022/HX:FILLN={fill}')
  np.unique(my_df["HX:BMODE"].dropna())
  
  dff = df
  
  
  for counter, ii in enumerate(range(0, 5000,200)):
  
  
      #for counter, ii in enumerate(range(0, 5000,200)):
  
      x_lims = mdates.date2num(dff.index.values)  
      #x_lims2 = mdates.date2num(dfmains2.index.values)  
      
      frev=11245.5
      #freqs = np.linspace(0, frev*2., len(dff["fourier"].iloc[0]))
      ############
      freqs = np.linspace(0, frev*2., len(dff["fourier"].iloc[0]))
      ############
      #freqs = dff.freqs.values[0]
      ################
      fourier_abs = np.array(dff.fourier.to_list())
      #############
      #fourier_abs = np.array(dff.fourier_abs.to_list())
      
      myfilter = (freqs>ii-10) & (freqs<ii+210) 
      #myfilter = (freqs>2980) & (freqs<3020)
      fig, ax = plt.subplots()
  
      
      
      #plt.imshow(np.array(np.log10(fourier_abs)[:, myfilter]), aspect='auto', cmap='jet', extent=[freqs[myfilter][0], freqs[myfilter][-1], x_lims[0], x_lims[-1]])
      ##plt.imshow(np.array(np.log10(fourier_abs)[:, myfilter]), aspect='auto', cmap='jet')
      
      
      plt.pcolormesh(freqs[myfilter], dff.index.values, np.array(np.log10(fourier_abs)[:, myfilter]), cmap='jet', shading='auto')
      
      #plt.plot(dfmains2.f.values, dfmains2.index.values, c='k', lw=5)
      
      #for i in range(50, 12000, 50):
      #    kk = i/50.
      #    plt.plot(i+(dfmains2.f.values-50.)*kk, dfmains2.index.values, c='b', lw=2)
      print(ax.get_xlim())
      #plt.plot([50. for i in dfmains2["f"]], dfmains2.index.values, lw=2, c='k')
      
      plt.xlim(freqs[myfilter][0], freqs[myfilter][-1])
      plt.ylim(dff.index.values[0], dff.index.values[-1])
      #plt.ylim(dff.index.values[0], dff.index.values[-1])
      plt.colorbar()
      ax.yaxis_date()
      date_format = mdates.DateFormatter('%H:%M:%S')
      ax.yaxis.set_major_formatter(date_format)
      plt.title(f'Fill {fill}, {beamplane}, {pu}')
      # This simply sets the x-axis data to diagonal so it fits better.
      fig.autofmt_xdate()
      plt.xlabel('f (Hz)')
      #plt.ylabel("UTC time 02/07/2022")
      #plt.ylabel("UTC time 06/07/2022")
      plt.ylabel("UTC time")
      
      
      
      
      for mode in ["PRERAMP", "RAMP", "FLATTOP", "ADJUST", "STABLE"]:#, "SQUEEZE", "STABLE"]:
          tt=pd.Timestamp(my_df[my_df["HX:BMODE"] == mode].iloc[0].name)
          plt.axhline(tt, c='k', lw=2)
          plt.text(ii, tt, mode, c='k', fontsize=18)
  
      
  
      
      fig.tight_layout()
      
      fig.savefig(f"{save_to}/plot_{counter}_{ii}Hz_{ii+200}Hz.png")
      #fig.savefig(f"plots_MD_latest/plot_{counter}_{ii}Hz_{ii+200}Hz.png")
      
      plt.close("all")
  
  dff = df
  
  
  for counter, ii in enumerate(range(0, 5000,200)):
  
      #for counter, ii in enumerate(range(0, 5000,200)):
  
      x_lims = mdates.date2num(dff.index.values)  
      #x_lims2 = mdates.date2num(dfmains2.index.values)  
      
      frev=11245.5
      #freqs = np.linspace(0, frev*2., len(dff["fourier"].iloc[0]))
      ############
      freqs = np.linspace(0, frev*2., len(dff["fourier"].iloc[0]))
      ############
      #freqs = dff.freqs.values[0]
      ################
      fourier_abs = np.array(dff.fourier.to_list())
      #############
      #fourier_abs = np.array(dff.fourier_abs.to_list())
      
      myfilter = (freqs<11245.5-(ii-10)) & (freqs>11245.5-(ii+210))
      #myfilter = (freqs>2980) & (freqs<3020)
      fig, ax = plt.subplots()
  
      
      
      #plt.imshow(np.array(np.log10(fourier_abs)[:, myfilter]), aspect='auto', cmap='jet', extent=[freqs[myfilter][0], freqs[myfilter][-1], x_lims[0], x_lims[-1]])
      ##plt.imshow(np.array(np.log10(fourier_abs)[:, myfilter]), aspect='auto', cmap='jet')
      
      
      plt.pcolormesh(freqs[myfilter], dff.index.values, np.array(np.log10(fourier_abs)[:, myfilter]), cmap='jet', shading='auto')
      
      #plt.plot(dfmains2.f.values, dfmains2.index.values, c='k', lw=5)
      
      #for i in range(50, 12000, 50):
      #    kk = i/50.
      #    plt.plot(i+(dfmains2.f.values-50.)*kk, dfmains2.index.values, c='b', lw=2)
      print(ax.get_xlim())
      #plt.plot([50. for i in dfmains2["f"]], dfmains2.index.values, lw=2, c='k')
      
      plt.xlim(freqs[myfilter][0], freqs[myfilter][-1])
      plt.ylim(dff.index.values[0], dff.index.values[-1])
      #plt.ylim(dff.index.values[0], dff.index.values[-1])
      plt.colorbar()
      ax.yaxis_date()
      date_format = mdates.DateFormatter('%H:%M:%S')
      ax.yaxis.set_major_formatter(date_format)
      plt.title(f'Fill {fill}, {beamplane}, {pu}')
      # This simply sets the x-axis data to diagonal so it fits better.
      fig.autofmt_xdate()
      plt.xlabel('f (Hz)')
      #plt.ylabel("UTC time 02/07/2022")
      plt.ylabel("UTC time")
  
  
      for mode in ["PRERAMP", "RAMP", "FLATTOP", "ADJUST", "STABLE"]:#, "SQUEEZE", "STABLE"]:
          tt=pd.Timestamp(my_df[my_df["HX:BMODE"] == mode].iloc[0].name)
          plt.axhline(tt, c='k', lw=2)
          plt.text(11245.5-(ii+210), tt, mode, c='k', fontsize=18)
      
  
      
      fig.tight_layout()
      
      fig.savefig(f"{save_to}/plot_{counter}.png")
      #fig.savefig(f"plots_MD_latest/plot_{counter}_{ii}Hz_{ii+200}Hz.png")
      
      plt.close("all")
