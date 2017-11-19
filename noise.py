import pickle
import metadata as md
import numpy as np

from noise_plot import *

# Select data wrt to condition for less than 25 mV and fill histograms for pedestals and noises
# Input: TH1-objects for pedestals and noises for each channel, and data points
def noiseAnalysis(data):
    
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    for entry in range(0,len(data)):
        for chan in channels:
            
            pulse_compatible_samples = data[entry][chan] > 25
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            noise_average[entry][chan] = np.average(data[entry][chan][0:max_index])
            noise_std[entry][chan] = np.std(data[entry][chan][0:max_index])

    return noise_average, noise_std


# Export pedestal info (noise analysis)
def exportNoiseInfo(pedestal, noise):

    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pedestal_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"wb") as output:
        pickle.dump(pedestal,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(noise,output,pickle.HIGHEST_PROTOCOL)


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importNoiseProperties():
    
    pedestal = ""
    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pedestal_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"rb") as input:
        pedestal = pickle.load(input)
        noise = pickle.load(input)

    return pedestal, noise


# Calculates pedestal and noise mean values per channel for all entries
def getPedestalNoisePerChannel(noise_average, noise_std):
    
    pedestal = dict()
    noise = dict()

    for chan in noise_average.dtype.names:
        pedestal[chan] = np.mean(noise_average[chan])
        noise[chan] = np.mean(noise_std[chan])
    
    return pedestal, noise
