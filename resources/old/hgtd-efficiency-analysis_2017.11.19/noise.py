
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import pandas as pd


# Select data wrt to condition for less than 25 mV and fill histograms for pedestals and noises
# Input: TH1-objects for pedestals and noises for each channel, and data points
#def noiseAnalysisPerFilePerChunk(filename, begin, end):
def noiseAnalysisPerFilePerChunk(data):
    
    #data = rnm.root2array( filename, start=begin, stop=end )
    
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    for entry in range(0,len(data)):
        for chan in channels:
            
            pulse_compatible_samples = data[entry][chan] > 25
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            average = np.average(data[entry][chan][0:max_index])
            std = np.std(data[entry][chan][0:max_index])
            
            noise_average[entry][chan] = average
            noise_std[entry][chan] = std

    return noise_average, noise_std
