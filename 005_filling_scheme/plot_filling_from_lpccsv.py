# csv can be found in https://lpc.web.cern.ch/cgi-bin/fillTable.py?year=2022
import csv
import numpy as np


filling_schemes = ["Single_3b_2_2_2.csv", 
                   "Single_12b_8_8_8_2018.csv",
                   "25ns_75b_62_32_62_12bpi_9inj.csv", 
                   #"25ns_387b_374_236_302_12bpi_35inj_3INDIV", 
                   #"25ns_411b_398_320_338_36bpi_15inj_3INDIV", 
                   #"25ns_399b_386_204_258_128bpi_7inj_hybrid_3INDIV", 
                   #"25ns_911b_898_555_690_128bpi_11inj_hybrid_3INDIV", 
                   #"25ns_959b_946_735_721_236bpi_9inj_hybrid_3INDIV", 
                   #"25ns_1195b_1182_735_721_236bpi_10inj_hybrid_3INDIV", 
                   #"25ns_1903b_1890_1259_1176_236bpi_hybrid_3INDIV",
                   #"25ns_2374b_2362_1686_1706_236bpi_13inj_hybrid_2INDIV"]
                    ]


for filling_scheme in filling_schemes[:]:
    with open(filling_scheme, 'r') as f:
        reader = csv.reader(f)
    
        head_on_b1 = {}
        head_on_b2 = {}
    
        for row in reader:
            if not row:
                continue 
            
            if 'HEAD ON COLLISIONS FOR B' in row[0]:
                beam = int(row[0][-1])
                next(reader)
                head_on_data = {}
                for row in reader:
                    if not row:
                        break
                    bucket, ip1, ip2, ip5, ip8 = row
                    bucket = int(bucket)
                    head_on_data[bucket] = {'IP1': ip1, 'IP2': ip2, 'IP5': ip5, 'IP8': ip8}
                if beam == 1:
                    head_on_b1 = head_on_data
                elif beam == 2:
                    head_on_b2 = head_on_data
            if row:
                if 'bucket number' in row[0]:
                    beam  = int((row[0][1]))
                    #next(reader)
                    head_on_data = {}
                    for row in reader:
                        if not row:
                            break
                        bucket, ip1, ip2, ip5, ip8 = row
                        bucket = int(bucket)
                        head_on_data[bucket] = {}
                    if beam == 1:
                        head_on_b1 = head_on_data
                    elif beam == 2:
                        head_on_b2 = head_on_data

    print(len(head_on_b1.keys()))
    #print(head_on_b1.keys())
    print(len(head_on_b2.keys()))
    #print(head_on_b2.keys())
    
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    plt.plot(np.arange(35640), [1 if bucket in head_on_b1.keys() else 0 for bucket in range(35640)], 'k')
    plt.xlabel("Bunch slot")
    plt.title(f"B1: {len(head_on_b1.keys())}, B2: {len(head_on_b2.keys())},{filling_scheme}")
    fig.savefig(f'{filling_scheme.split(".")[0]}.png')
    plt.show()
