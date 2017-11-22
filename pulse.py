import pickle
import numpy as np
import sys

import noise as ns
import metadata as md


# The code obtains amplitudes and rise time for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "rise_time".
def pulseAnalysis(data, noise_average, noise_std):
   
    channels = data.dtype.names
    
    amplitudes = np.zeros(len(data), dtype = data.dtype)
    rise_times = np.zeros(len(data), dtype = data.dtype)
    
    pedestal, noise = ns.getPedestalAndNoisePerChannel(noise_average, noise_std)
    
    for entry in range(0,len(data)):
        for chan in channels:
            amplitudes[entry][chan], rise_times[entry][chan] = getAmplitudeAndRiseTime(data[chan][entry], chan, pedestal[chan], noise[chan])

    return amplitudes, rise_times


def getAmplitudeAndRiseTime(event, chan, pedestal, noise):
    
    timeScope = 0.1 # For all files
    
    pulse_amplitude = 0
    pulse_rise_time = 0
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

    return pulse_amplitude, pulse_rise_time


# Function which removes amplitudes which are in the range being critical amplitude values
def removeUnphyscialAmplitudes(amplitudes, rise_times, pedestal, noise):

    criticalValues = findCriticalValues(amplitudes, pedestal)
  
    for chan in amplitudes.dtype.names:
      
        indices = amplitudes[chan] < criticalValues[chan]*0.98
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        
        indices = amplitudes[chan] > noise[chan]*-sigmaConstant
        amplitudes[chan][indices] = 0

    return amplitudes, rise_times, criticalValues


# Search for critical amplitude values
def findCriticalValues(data, pedestal):
    
    channels = data.dtype.names
    criticalValues = dict()

    for chan in channels:
        criticalValues[chan] = 0

    for chan in channels:
        for entry in range(0,len(data)):
            if criticalValues[chan] > np.amin(data[chan][entry]):
                criticalValues[chan] = np.amin(data[chan][entry])

    for chan in channels:
        criticalValues[chan] -= pedestal[chan]

    return criticalValues



def exportPulseData(amplitudes, rise_times):

    with open("../../HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_data/pulse_data_"+str(md.getRunNumber())+".pkl","wb") as output:
        
        pickle.dump(amplitudes,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(rise_times,output,pickle.HIGHEST_PROTOCOL)


def exportCriticalValues(criticalValues):

    with open("../../HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_critical_values/pulse_critical_values_"+str(md.getRunNumber())+".pkl","wb") as output:
        
        pickle.dump(criticalValues,output,pickle.HIGHEST_PROTOCOL)
        
        
# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importPulseInfo():

    # Note: amplitude values are corrected with a pedestal (from the noise analysis) and the critical values are not
    with open("../../HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_data/pulse_data_"+str(md.getRunNumber())+".pkl","rb") as input:
        
        amplitude = pickle.load(input)
        rise_time = pickle.load(input)
    
    with open("../../HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_critical_values/pulse_critical_values_"+str(md.getRunNumber())+".pkl","rb") as input:
    
        criticalValues = pickle.load(input)


    return amplitude, rise_time, criticalValues


def defineSigmaConstant(sigma):

    global sigmaConstant
    sigmaConstant = sigma



