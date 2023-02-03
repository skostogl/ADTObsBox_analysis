# Important paths & info

## From G.Sterbini:
- Nx2pd: https://gitlab.cern.ch/lhclumi/lumi-followup/-/tree/master/examples/nx2pd
- tree_maker: https://gitlab.cern.ch/abpcomputing/sandbox/tree_maker

## Variable names in nxcals:
ObsBox2Spectrum.LHC.ADT.REAL.{beamplane}.Q7:acquisitionCorrected:acquisition

# Steps for analysis
- This analysis has been tested in afs with htcondor
1. Run 000_fills.py after specifying a time interval t0 and t1 to create fills.parquet which contains all fill numbers, modes and number of bunches
2. Run 001_make_folders to create tree with all fills specified in fills.parquet. Each job has $chunks_per_job fills. In this file, the study name, path to save the plots (for example in eos) and the python path are specified.
3. Run 002_chronjob.py: Specify 'tree_maker_$studyname.json' and submit jobs to htcondor
