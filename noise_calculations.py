import ROOT
import pickle
import numpy as np
import root_numpy as rnm
import os

import metadata as md

# Calculate the noise for all channels
def findNoiseAverageAndStd(dataPath, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    for event in range(0,len(data)):
        for chan in channels:
        
            ####################################################################
            #
            #   Two conditions of selecting the pedestal and noise:
            #       1. pulse_limit = limit of exceeding the noise
            #       2. data_point_correction = 'going back' couple of points
            #
            #   The limit is chosen from observing the waveform, the data point
            #   correction is a convention to make the code more reliable
            #
            ####################################################################

            pulse_limit = -25 * 0.001 # mV
            data_point_correction = 3
            
            pulse_compatible_samples = data[event][chan] < pulse_limit
            max_index = np.where(pulse_compatible_samples)[0][0] - data_point_correction if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            noise_average[event][chan] = np.average(data[event][chan][0:max_index])
            noise_std[event][chan] = np.std(data[event][chan][0:max_index])


    return noise_average, noise_std


# Calculates pedestal and noise mean values per channel for all entries
def getPedestalAndNoisePerChannel(noise_average, noise_std):
    
    pedestal = dict()
    noise = dict()

    for chan in noise_average.dtype.names:
        pedestal[chan] = np.mean(noise_average[chan])
        noise[chan] = np.mean(noise_std[chan])
    
    return pedestal, noise


# Convert to positive values in mV
def convertNoise(noise_average, noise_std):
  
    channels = noise_average.dtype.names
  
    for chan in channels:
    
        noise_average[chan] =   np.multiply(noise_average[chan], -1000)
        noise_std[chan]     =   np.multiply(noise_std[chan], 1000)
    
    return noise_average, noise_std


