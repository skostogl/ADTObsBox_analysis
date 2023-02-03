import os
import getpass
import logging
import sys
import numpy as np
import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.environ['PYSPARK_PYTHON'] = "./environment/bin/python"
username = getpass.getuser()
print(f'Assuming that your kerberos keytab is in the home folder, ' 
      f'its name is "{getpass.getuser()}.keytab" '
      f'and that your kerberos login is "{username}".')

logging.info('Executing the kinit')
os.system(f'kinit -f -r 5d -kt {os.path.expanduser("~")}/{getpass.getuser()}.keytab {getpass.getuser()}');

# %%
import json
import nx2pd as nx 
import pandas as pd

from nxcals.spark_session_builder import get_or_create, Flavor

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


df_fills = pd.read_parquet("fills.parquet")
if df_fills['HX:FILLN'].iloc[0] == None:
  df_fills['HX:FILLN'].iloc[0] = df_fills['HX:FILLN'].dropna().iloc[0]
df_fills['HX:FILLN'] = df_fills['HX:FILLN'].ffill(axis=0)

print(df_fills['HX:FILLN'].unique())

fills = ["8496"]#df_fills['HX:FILLN'].unique()
save_to = 'from_nxclals_spectrum'

try:
    os.makedirs(save_to)
except FileExistsError:
    pass

for current_fill in fills:
  #for beamplane in ["B1H", "B1V", "B2H", "B2V"]:
  for beamplane in ["B1H"]:
      try:
        print(current_fill, beamplane)
        try:
          df_current = df_fills[df_fills['HX:FILLN'] == current_fill]
          print(df_current)  
          print(df_current['HX:BMODE'].dropna(), df_current['LHC.BQM.B1:NO_BUNCHES'].dropna().max())
          t0 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'INJPHYS'].index[0])
          try:
            t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'BEAMDUMP'].index[0])
          except Exception as e:
            t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] ==df_current['HX:BMODE'].dropna().iloc[-1]].index[-1])
          if current_fill=='8211':
            t1 = pd.Timestamp(df_current[df_current['HX:BMODE'] == 'BEAMDUMP'].index[-1])

          # split into 5h intervals if needed
          print(t0, t1)
          interval = datetime.timedelta(minutes=60*1)
          periods = []
          period_start = t0
          while period_start < t1:
              period_end = min(period_start + interval, t1)
              periods.append((period_start, period_end))
              period_start = period_end

        except Exception as e:
          print('Error! ', beamplane, current_fill, e)
          continue
        data_list = [f"ObsBox2Spectrum.LHC.ADT.REAL.{beamplane}.Q7:acquisitionCorrected:acquisition"]
        appended_df = []
        for i in range(0, len(periods)):
          print(data_list,periods[i][0],periods[i][1])
          df = sk.nxcals_df(data_list,periods[i][0],periods[i][1],pandas_processing=[nx.pandas_get,nx.pandas_pivot,])
          appended_df.append(df)
        try:
          df = pd.concat(appended_df, axis=0)
          tfirst = pd.Timestamp(df.iloc[0].name)
          tlast = pd.Timestamp(df.iloc[-1].name)
        except Exception as e:
            print('Empty df! ', e)
            continue
        print(tfirst, tlast)
        df.to_parquet(f"{save_to}/FFT_{current_fill}_{beamplane}_{tfirst}_{tlast}.parquet")
      except Exception as e:
          print("Error! ", beamplane, current_fill, e)
