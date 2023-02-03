import os
import json
import getpass
import logging
import sys
import numpy as np
import datetime
import yaml
import tree_maker
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
import glob
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
'figure.figsize': (12, 11),
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

import nx2pd as nx 
from nxcals.spark_session_builder import get_or_create, Flavor

with open("config.yaml", "r") as f:
      config = yaml.safe_load(f)

# Download spectrum from nxcals
if True:
  logging.basicConfig(stream=sys.stdout, level=logging.INFO)
  
  os.environ['PYSPARK_PYTHON'] = "./environment/bin/python"
  username = getpass.getuser()
  print(f'Assuming that your kerberos keytab is in the home folder, ' 
        f'its name is "{getpass.getuser()}.keytab" '
        f'and that your kerberos login is "{username}".')
  
  logging.info('Executing the kinit')
  os.system(f'kinit -f -r 5d -kt {os.path.expanduser("~")}/{getpass.getuser()}.keytab {getpass.getuser()}');
   
  logging.info('Creating the spark instance')
  #spark = get_or_create(flavor=Flavor.LOCAL)
  spark = get_or_create(flavor=Flavor.LOCAL,                                         
  conf={'spark.driver.maxResultSize': '8g',                                          
      'spark.executor.memory':'8g',                                                  
      'spark.driver.memory': '16g',                                                  
      'spark.executor.instances': '20',                                              
      'spark.executor.cores': '2',                                                   
      })                                                                             
    
  #spark = get_or_create(flavor=Flavor.YARN_SMALL, master='yarn')
  sk  = nx.SparkIt(spark)
  logging.info('Spark instance created.')
   
  df_fills = pd.read_parquet(config["fills_path"])
  if df_fills['HX:FILLN'].iloc[0] == None:
    df_fills['HX:FILLN'].iloc[0] = df_fills['HX:FILLN'].dropna().iloc[0]
  df_fills['HX:FILLN'] = df_fills['HX:FILLN'].ffill(axis=0)
  
  fills = config["fill_nb"]#['8496']
  for current_fill in fills:
    for beamplane in ["B1H", "B1V", "B2H", "B2V"]:
        try:
          print(current_fill, beamplane)
          try:
            #if True:
            df_current = df_fills[df_fills['HX:FILLN'] == current_fill]
            print(df_current)  
            print(df_current['HX:BMODE'].dropna(), df_current['LHC.BQM.B1:NO_BUNCHES'].dropna().max())
            t0 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'INJPHYS'].index[0])
            try:
              t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'BEAMDUMP'].index[0])
            except:
              t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] ==df_current['HX:BMODE'].dropna().iloc[-1]].index[-1])
  
            # split into 5h intervals if needed
            print(t0, t1, "time range")
            interval = datetime.timedelta(minutes=60*1)
            periods = []
            period_start = t0
            while period_start < t1:
                period_end = min(period_start + interval, t1)
                periods.append((period_start, period_end))
                period_start = period_end
           
            #print(t0,t1, current_fill)
          except:
            print('prob', beamplane, current_fill)
            continue
          data_list = [f"ObsBox2Spectrum.LHC.ADT.REAL.{beamplane}.Q7:acquisitionCorrected:acquisition"]
          #try:
          appended_df = []
          for i in range(0, len(periods)):
            #for i in range(0, 1):
            #df = sk.nxcals_df(["ObsBox2Spectrum.LHC.ADT.REAL.B1V.Q7:acquisition:SpectrumAmplitudeAvgCorrected"],
            print(data_list,periods[i][0],periods[i][1])
            df = sk.nxcals_df(data_list,periods[i][0],periods[i][1],pandas_processing=[nx.pandas_get,nx.pandas_pivot,])
            #print(df)
            appended_df.append(df)
          try:
            #if True:
            df = pd.concat(appended_df, axis=0)
            tfirst = pd.Timestamp(df.iloc[0].name)
            tlast = pd.Timestamp(df.iloc[-1].name)
          except:
              print('empty df')
              continue
          print(tfirst, tlast)
          df.to_parquet(f"FFT_{current_fill}_{beamplane}_{tfirst}_{tlast}.parquet")
        except:
            print("prob", beamplane, current_fill)
  

# Plot spectra

fills = config["fill_nb"]

path = "."
for fill_nb in fills:

    if fill_nb == '8182':
        plot_beam_mode = False
    else:
        plot_beam_mode = True
    
    
    for beam_plane in ['B1H', 'B2H', 'B1V', 'B2V']:
    
      try:
        #beam_plane = 'B2H'

        file = glob.glob(f"{path}/*{fill_nb}*{beam_plane}*")[0]
        print(file)
        df = pd.read_parquet(file)
        df[df.columns[0]] = df[df.columns[0]].apply(lambda x: x['elements'])
        df.index = [pd.Timestamp(df.index[i]) for i in range(len(df))]
        print(df)


        df_fills = pd.read_parquet(config["fills_path"])
        if df_fills['HX:FILLN'].iloc[0] == None:
          df_fills['HX:FILLN'].iloc[0] = df_fills['HX:FILLN'].dropna().iloc[0]
        df_fills['HX:FILLN'] = df_fills['HX:FILLN'].ffill(axis=0)
        df_fills = df_fills[df_fills['HX:FILLN'] == fill_nb]
        df_fills.index = [pd.Timestamp(df_fills.index[i]) for i in range(len(df_fills))]
        print(df_fills)

        df_bunches = df_fills[f'LHC.BQM.B{beam_plane[1:2]}:NO_BUNCHES'].dropna().astype(int)
        bunches = df_bunches.max()

        myeos=config["save_to"]
        save_to  = f"{myeos}/plots_{fill_nb}"
        from pathlib import Path
        Path(save_to).mkdir(parents=True, exist_ok=True)

        save_to  = f"{myeos}/plots_{fill_nb}/{beam_plane}"
        from pathlib import Path
        Path(save_to).mkdir(parents=True, exist_ok=True)    


        for counter, ii in enumerate(range(0, 5000,200)):#(range(0, 5000,200)):

            x_lims = mdates.date2num(df.index.values)  

            frev=11245.5
            freqs = np.linspace(0, frev, len(df[df.columns[0]].iloc[0]))
            fourier_abs = np.array(df[df.columns[0]].to_list())

            ################################################
            myfilter = (freqs>ii-10) & (freqs<ii+210) 
            fig, ax = plt.subplots()
            plt.pcolormesh(freqs[myfilter], df.index.values, np.array(np.log10(fourier_abs)[:, myfilter]), cmap='jet', shading='auto')
            plt.xlim(freqs[myfilter][0], freqs[myfilter][-1])
            plt.ylim(df.index.values[0], df.index.values[-1])
            #plt.colorbar()
            ax.yaxis_date()
            date_format = mdates.DateFormatter('%H:%M:%S')
            ax.yaxis.set_major_formatter(date_format)
            plt.title(f'Fill {fill_nb}, {beam_plane}, {bunches} bunches')
            fig.autofmt_xdate()
            plt.xlabel('f (Hz)')
            plt.ylabel(f"UTC time {df.index[0].day}/{df.index[0].month}/{df.index[0].year}")

            if plot_beam_mode:
                for mode in ["PRERAMP", "RAMP", "FLATTOP", "ADJUST", "STABLE"]:#, "SQUEEZE", "STABLE"]:
                    try:
                        tt=pd.Timestamp(df_fills[df_fills["HX:BMODE"] == mode].iloc[0].name)
                        print(tt)
                        plt.axhline(tt, c='k', lw=2)
                        plt.text(ii, tt, mode, c='k', fontsize=18)
                    except:
                        print('prob', mode)

            fig.tight_layout()
            fig.savefig(f"{save_to}/plot_{counter}_{ii}Hz_{ii+200}Hz.png")
            plt.close("all")

            #############################################
            myfilter = (freqs<11245.5-(ii-10)) & (freqs>11245.5-(ii+210))
            fig, ax = plt.subplots()
            plt.pcolormesh(freqs[myfilter], df.index.values, np.array(np.log10(fourier_abs)[:, myfilter]), cmap='jet', shading='auto')
            plt.xlim(freqs[myfilter][0], freqs[myfilter][-1])
            plt.ylim(df.index.values[0], df.index.values[-1])
            #plt.colorbar()
            ax.yaxis_date()
            date_format = mdates.DateFormatter('%H:%M:%S')
            ax.yaxis.set_major_formatter(date_format)
            plt.title(f'Fill {fill_nb}, {beam_plane}, {bunches} bunches')
            fig.autofmt_xdate()
            plt.xlabel('f (Hz)')
            plt.ylabel(f"UTC time {df.index[0].day}/{df.index[0].month}/{df.index[0].year}")

            if plot_beam_mode:
                for mode in ["PRERAMP", "RAMP", "FLATTOP", "ADJUST", "STABLE"]:#, "SQUEEZE", "STABLE"]:
                    try:
                        tt=pd.Timestamp(df_fills[df_fills["HX:BMODE"] == mode].iloc[0].name)
                        print(tt)
                        plt.axhline(tt, c='k', lw=2)
                        plt.text(11245.5-(ii+210), tt, mode, c='k', fontsize=18)
                    except:
                        print('prob', mode)


            fig.tight_layout()
            fig.savefig(f"{save_to}/plot_{counter}_{11245.5-(ii+210)}Hz_{11245.5-(ii-10)}Hz.png")
            plt.close("all")
      except:
            print('prob')


tree_maker.tag_json.tag_it(config['log_file'], 'completed')

