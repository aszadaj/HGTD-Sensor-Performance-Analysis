
import ROOT
import pickle
import numpy as np
import root_numpy as rnm
import os

import metadata as md

# Data input description
#
# x-value = time: ranges between 0 and 100.2 ns
# difference between two points is 0.1 ns -> 1002 data points in each entry)

# y-value = voltage: expressed in V, with negative values as pulses
# difference betwen two points is 1.31651759148e-05 V ~ 0.013 mV
# Data have the structure per channels (up to 8 different) and each with 200 000 entries, can be
# customizable

def findNoiseAverageAndStd(data):
   
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    count = 0
    
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
            
            # The SiPM behaves differently, in general I think that the limits should be adapted for each sensor
            # W4-RD01 in batch 306 behaves strange, choose different batch to make different analysis, since
            # the waveforms behaves differently than predicted
        
            # Consider points until a pulse
            pulse_limit = 25 * 0.001 # mV
            data_point_correction = 3
            # Take out points which are above the noise level
            pulse_compatible_samples = -data[event][chan] > pulse_limit
            
            # Select the "last index" which defines the range of the noise selection
            max_index = np.where(pulse_compatible_samples)[0][0] - data_point_correction if len( np.where(pulse_compatible_samples)[0] ) else 1002

            noise_average[event][chan] = np.average(data[event][chan][0:max_index])
            noise_std[event][chan] = np.std(data[event][chan][0:max_index])


    return noise_average, noise_std


# Calculates pedestal and noise mean values per channel for all entries
def getPedestalAndNoisePerChannel(noise_average, noise_std):
    
    channels = noise_average.dtype.names
    
    pedestal = np.empty(1, dtype=noise_average.dtype)
    noise = np.empty(1, dtype=noise_average.dtype)

    for chan in channels:
    
        pedestal[chan] = np.mean(noise_average[chan])
        noise[chan] = np.mean(noise_std[chan])

    return pedestal, noise


# Convert to positive values in mV
def convertNoise(results):

    channels = results[0][0].dtype.names
    
    noise_average   = np.empty(0, dtype=results[0][0].dtype)
    noise_std       = np.empty(0, dtype=results[0][1].dtype)
    
    for index in range(0, len(results)):
        noise_average   = np.concatenate((noise_average, results[index][0]), axis = 0)
        noise_std       = np.concatenate((noise_std, results[index][1]), axis = 0)
    
    for chan in channels:
        noise_average[chan] = np.multiply(noise_average[chan], -1000)
        noise_std[chan] = np.multiply(noise_std[chan], 1000)
    
    return [noise_average, noise_std]



