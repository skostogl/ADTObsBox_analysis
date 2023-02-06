- 000b_create_file_list.py: finds all relevant h5 filenames between t1 and t2. t1 and t2 can be extracted from fill info from fills.parquet (run 000_fills.py to create it) or the user can define this time range. The user can also select subsampling.
- 001_make_folders.py: create tree
- 002_chronjob.py: submit to htcondor
- master_jobs: the template files

