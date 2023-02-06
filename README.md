# Useful tools
- tree_maker: https://gitlab.cern.ch/abpcomputing/sandbox/tree_maker
- MD scripts: https://gitlab.cern.ch/abpcomputing/sandbox/md6823
- ADTObsBox path: /nfs/cfc-sr4-adtobs2buf/obsbox/slow
- RTE data: https://www.services-rte.com/en/download-data-published-by-rte.html?category=public_transmission_system&type=network_frequencies

# How to use
The scripts are organized in the following way:
- 000_simple_example.ipynb: a simple example that explains basic concepts with sine signals and presents the way to combine bbb data. 
- 001_readh5.py: a simple example to read an .h5 file from the ADTObsBox measurements
- 002_submit_analysis_htcondor: how to submit .h5 analysis in htcondor
- 003_spectrum_from_nxcals: a simple example to extract the spectrum from nxcals
- 004_nxcals_htcondor: how to submit nxcals extraction analysis and ploting in htcondor
- mount_nfs.sh: mount path of ADTObsBox data in nfs
- useful_tools: class to read adt data and compute the fft

