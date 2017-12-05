import numpy as np

import metadata as md
import data_management as dm


# The code obtains amplitudes and rise time for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "rise_time".
def pulseAnalysis(data, pedestal, noise):
   
    channels = data.dtype.names
    
    amplitudes = np.zeros(len(data), dtype = data.dtype)
    rise_times = np.zeros(len(data), dtype = data.dtype)
    peak_times = np.zeros(len(data), dtype = data.dtype)
    
    for event in range(0,len(data)):
    
        for chan in channels:
        
            amplitudes[event][chan], rise_times[event][chan], peak_times[chan] = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001)
   
    return amplitudes, rise_times, peak_times


# Calculate maximum amplitude value and rise time, if found.
def getAmplitudeAndRiseTime(event, chan, pedestal, noise):
   
    timeScope = 0.1 # For all files
    
    pulse_amplitude = 0
    pulse_rise_time = 0
    pulse_last_index = 0
    indices_condition = event < noise * -sigmaConstant
   
    if any(indices_condition):
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmin(event)
        pulse_amplitude = np.amin(event) - pedestal
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index] > 0.9*np.amin(event)) & (event[pulse_first_index:pulse_last_index] < 0.1*np.amin(event)))
        
        pulse_rise_time = len(amplitude_indices)*timeScope
        
        if len(amplitude_indices) == 0:
            pulse_amplitude = 0
            pulse_last_index = 0

    return pulse_amplitude, pulse_rise_time, pulse_last_index*timeScope


# Function which removes amplitudes which are in the range being critical amplitude values
# NOTE THIS FUNCTION HANDLES CONVERTED DATA (I.E. NEGATIVE TO POSITIVE VALUES AND IN mV)
def removeUnphyscialQuantities(results, noise):

    amplitudes, rise_times, peak_times = [i for i in results]

    criticalValues = findCriticalValues(amplitudes)
    
    for chan in amplitudes.dtype.names:
      
        indices = amplitudes[chan] > criticalValues[chan]*0.98
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        peak_times[chan][indices] = 0
        
        indices = amplitudes[chan] < noise[chan]*sigmaConstant
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        peak_times[chan][indices] = 0

    return amplitudes, rise_times, criticalValues, peak_times


# Search for critical amplitude values
def findCriticalValues(data):

    data = convertData(data)

    noise = dm.importNoiseFile("noise")
    channels = data.dtype.names
    
    criticalValues = dict()

    for chan in channels:
        criticalValues[chan] = 0

    for chan in channels:
        for event in range(0,len(data)):
            if criticalValues[chan] < np.amin(data[chan][event]):
                criticalValues[chan] = np.amin(data[chan][event])

    return criticalValues


# Convert to positive values in mV
def convertData(data):
  
    channels = data.dtype.names
  
    for chan in channels:
        data[chan] = np.multiply(data[chan],-1000)
    
    return data


# Define sigma value
def defineSigmaConstant(sigma):

    global sigmaConstant
    sigmaConstant = sigma


# Get sigma value
def getSigmaConstant():
    return sigmaConstant


