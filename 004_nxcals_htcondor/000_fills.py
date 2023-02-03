# From G. Sterbini https://gitlab.cern.ch/lhclumi/lumi-followup/-/tree/master/examples/nx2pd
# install nx2pd from https://gitlab.cern.ch/lhclumi/lumi-followup/-/tree/master/examples/nx2pd
import os
import getpass
import logging
import sys

import json
import nx2pd as nx 
import pandas as pd

from nxcals.spark_session_builder import get_or_create, Flavor

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.environ['PYSPARK_PYTHON'] = "./environment/bin/python"
username = getpass.getuser()
print(f'Assuming that your kerberos keytab is in the home folder, ' 
      f'its name is "{getpass.getuser()}.keytab" '
      f'and that your kerberos login is "{username}".')

logging.info('Executing the kinit')
os.system(f'kinit -f -r 5d -kt {os.path.expanduser("~")}/{getpass.getuser()}.keytab {getpass.getuser()}');

logging.info('Creating the spark instance')

# Here I am using YARN (to do compution on the cluster)
#spark = get_or_create(flavor=Flavor.YARN_SMALL, master='yarn')

# Here I am using the LOCAL (assuming that my data are small data,
# so the overhead of the YARN is not justified)
# WARNING: the very first time you need to use YARN
spark = get_or_create(flavor=Flavor.LOCAL)

logging.info('Creating the spark instance')
spark = get_or_create(flavor=Flavor.LOCAL)
#spark = get_or_create(flavor=Flavor.YARN_SMALL, master='yarn')
sk  = nx.SparkIt(spark)
logging.info('Spark instance created.')


t0 = pd.Timestamp('2022-10-23 00:00:13', tz='CET')
t1 = pd.Timestamp('2022-12-02 16:00', tz='CET')
#t1 = pd.Timestamp.now(tz='CET')

df = sk.nxcals_df(["HX:FILLN", "HX:BMODE", "LHC.BQM.B%:NO_BUNCHES"], 
                  t0,
                  t1,
                  pandas_processing=[
                     nx.pandas_get, 
                     nx.pandas_pivot, 
                     ]
                 )
print(df)
df.to_parquet("fills.parquet")
