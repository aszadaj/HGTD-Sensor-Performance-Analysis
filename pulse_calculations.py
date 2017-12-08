
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
        
            amplitudes[event][chan], rise_times[event][chan], peak_times[event][chan] = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001)

    return amplitudes, rise_times, peak_times


# Calculate maximum amplitude value and rise time, if found.
def getAmplitudeAndRiseTime(event, chan, pedestal, noise):
   
    timeScope = 0.1 # For all files, in nanoseconds. Each entry is 100.2 ns
    
    pulse_amplitude = 0
    pulse_rise_time = 0
    pulse_last_index = 0
    indices_condition = event < noise * -8 # sigma
   
    if any(indices_condition):
    
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmin(event)
        pulse_amplitude = np.amin(event) - pedestal

        amplitude_truth = (event[pulse_first_index:pulse_last_index] > 0.9*np.amin(event) ) & (event[pulse_first_index:pulse_last_index] < 0.1*np.amin(event))
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index] > 0.9*np.amin(event)) & (event[pulse_first_index:pulse_last_index] < 0.1*np.amin(event)))
        
        # Check if there are more than two points in the polyfit
        if len(amplitude_indices) > 2:

            coeff = np.polyfit(amplitude_indices.flatten()*timeScope, event[pulse_first_index:pulse_last_index][amplitude_truth].flatten(), 1)
            pulse_rise_time = (np.amin(event)*0.8)/coeff[0] # Solution for first degree polynomial fit, Amplitude(y) = p[0]*time(x) + p[1], where p is from polyfit
        
        else:
            pulse_amplitude = 0
            pulse_last_index = 0

    return pulse_amplitude, pulse_rise_time, pulse_last_index*timeScope


# Function which removes amplitudes which are in the range being critical amplitude values
# NOTE THIS FUNCTION HANDLES CONVERTED DATA (I.E. NEGATIVE TO POSITIVE VALUES AND IN mV)
# NOTE2 Here the amplitude values are pedestal corrected
def removeUnphyscialQuantities(results, noise):

    # There is a more beautiful fix, with nesting for loops, not important for now
    amplitudes = np.empty(0,dtype=results[0][0].dtype)
    rise_times = np.empty(0,dtype=results[0][1].dtype)
    peak_times = np.empty(0,dtype=results[0][2].dtype)
    
    for index in range(0, len(results)):
        amplitudes = np.concatenate((amplitudes, results[index][0]), axis=0)
        rise_times = np.concatenate((rise_times, results[index][1]), axis=0)
        peak_times = np.concatenate((peak_times, results[index][2]), axis=0)
    
    criticalValues = findCriticalValues(amplitudes)

    for chan in amplitudes.dtype.names:
      
        indices = amplitudes[chan] <= criticalValues[chan]
      
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        peak_times[chan][indices] = 0
        
        # Noise is in mV since imported from earlier program, future fix
        indices = amplitudes[chan] > noise[chan]*0.001*8 # sigma
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        peak_times[chan][indices] = 0

    return [convertData(amplitudes), rise_times, peak_times, convertData(criticalValues)]


# Search for critical amplitude values

def findCriticalValues(data):

    channels = data.dtype.names
    
    criticalValues = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        criticalValues[chan] = np.amin(data[chan])
    
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


