
import numpy as np
import pickle
import pandas as pd


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def pulseAnalysisPerFilePerChunk(runNumber, timeStamp, data, timeScope, pedestal, noise):
  
    amplitudes, risetimes, small_amplitudes = getPulseInfo(data, timeScope, runNumber, pedestal, noise)

    return amplitudes, risetimes, small_amplitudes


# Creates dictionaries for amplitudes and rise time where each key defines the channel and for each key
# there is a list of obtained amplitudes, where each index corresponds to an entry.
# E.g amplitudes["chan1"][233]: amplitude value for channel chan0 and entry 233
def getPulseInfo(data, timeScope, runNumber, pedestal, noise):
    
    channels = data.dtype.names
    
    amplitudes = np.zeros(len(data), dtype = data.dtype)
    risetimes = np.zeros(len(data), dtype = data.dtype)
    small_amplitudes = np.zeros(len(data), dtype = data.dtype)
       
    for entry in range(0,len(data)):
        for chan in channels:
            
            amplitudes[entry][chan], risetimes[entry][chan], small_amplitudes[entry][chan] = getAmplitudeRisetime(data[entry][chan], pedestal[chan],noise[chan], chan, entry, timeScope)

    return amplitudes, risetimes, small_amplitudes


# Calculates amplitude and rise time for selected entry and channel. It returns a zero value if:
def getAmplitudeRisetime (event, pedestal,noise, chan, entry, timeScope):
    
    ### The noise limit have to set individually per channel ###
    # Idea, get this from standard deviation, from noise program
    
    noise_limit = noise*10 # Limit to select amplitudes above the noise level
    
    # Set condition on finding the pulse, and select indices where the pulse is.
    indices_condition = event > noise_limit
    
    pulse_amplitude = 0
    pulse_risetime = 0
    small_amplitude = 0
    
    if any(indices_condition):
        
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmax(event)
        pulse_amplitude = np.amax(event)-pedestal
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]<0.9*np.amax(event)) & (event[pulse_first_index:pulse_last_index]>0.1*np.amax(event)))
        
        try:
            pulse_risetime = (amplitude_indices[-1][0] - amplitude_indices[0][0])*timeScope
        
        except Exception, e:
            small_amplitude = pulse_amplitude
            pulse_amplitude = 0
            pulse_risetime = 0

    return pulse_amplitude, pulse_risetime, small_amplitude

