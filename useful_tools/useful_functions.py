import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h5py
import datetime

class ADT:
    def __init__(self, filenames):
        df = self.extract_file_info(filenames)
        df.sort_index(inplace=True)
        self.importEmptyDF = {bp: df[df['Beam-Plane'] == bp] for bp in np.unique(df['Beam-Plane'])}

    def extract_file_info(self, filenames):
        beam_planes = []
        pus = []
        times = []
        for file_name in filenames:
            bp, pu, date, time = file_name.split('/')[-1].split('_')
            time = self.fromName2Timestamp(f'{bp}_{pu}_{date}_{time}')
            beam_planes.append(bp)
            pus.append(pu)
            times.append(time)
        return pd.DataFrame({'PU': pus, 'Beam-Plane': beam_planes, 'Path': filenames}, index=np.array(times))

    def fromName2Timestamp(self, current_fileName,tz_start='CET',tz_end='UTC'):
        year = current_fileName.split('_')[-2][0:4]
        month = current_fileName.split('_')[-2][4:6]
        day   = current_fileName.split('_')[-2][6:]
        full_datetime = f'{day}/{month}/{year} ' + current_fileName.split('_')[-1].split('.')[0]
        return pd.Timestamp(datetime.datetime.strptime(full_datetime,"%d/%m/%Y %Hh%Mm%Ss%fus")).tz_localize(tz_start, ambiguous=False).tz_convert(tz_end)

    def loadData(self, fileName):
        fi = h5py.File(fileName, 'r')
        beam, plane = fileName.split('_')[-4].split('/')[-1][:2], fileName.split('_')[-4].split('/')[-1][2:3]
        plane = 'horizontal' if plane == 'H' else 'vertical'
        alldat = fi[beam][plane]
        print('Buffer: Turns = %s, Bunches = %s' % (alldat.shape[0], alldat.shape[1]))
        return alldat[:]
    
    def cmp_fft(self, data, specific_bunch, frev=11245.5, first_bunch_slot=0, bunch_spacing=25e-9, repeat_fft=1):
        fourier =  np.fft.fft(data[:,specific_bunch] )
        fourier = fourier/len(fourier)*2.0
        delay   = (specific_bunch-first_bunch_slot)*bunch_spacing
        fourier = np.concatenate([fourier]*repeat_fft)
        freqs   = np.linspace(0, frev*repeat_fft, len(fourier))
        corrected_fourier = fourier*np.exp(-1j*2.0*np.pi*freqs*delay)
        return pd.Series([freqs, fourier.real, fourier.imag, corrected_fourier.real, corrected_fourier.imag])
    
