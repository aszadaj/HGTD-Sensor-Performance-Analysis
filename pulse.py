import pickle
import metadata as md
import numpy as np
import noise as ns


# The code obtains amplitudes and rise time for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "rise_time".
def pulseAnalysis(data, noise_average, noise_std):
   
    channels = data.dtype.names
    
    amplitudes = np.zeros(len(data), dtype = data.dtype)
    rise_times = np.zeros(len(data), dtype = data.dtype)
    
    for entry in range(0,len(data)):
        for chan in channels:
            amplitudes[entry][chan], rise_times[entry][chan] = getAmplitudeRiseTime(data[chan][entry], chan, noise_average, noise_std)
    
    return amplitudes, rise_times


# Calculates amplitude and rise time for selected entry and channel. It returns a zero value if:
def getAmplitudeRiseTime(event, chan, noise_average, noise_std):
    
    pedestal, noise = ns.getPedestalNoisePerChannel(noise_average, noise_std)

    pulse_amplitude = pulse_rise_time = 0
    indices_condition = event > noise[chan]*10
  
    if any(indices_condition):
        
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmax(event)
        pulse_amplitude = np.amax(event)
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]<0.9*np.amax(event)) & (event[pulse_first_index:pulse_last_index]>0.1*np.amax(event)))
     
        pulse_rise_time = len(amplitude_indices)*md.getTimeScope()
        
        if len(amplitude_indices) == 0:
            pulse_amplitude = 0

    return pulse_amplitude, pulse_rise_time


# Function which removes amplitudes which are in the range being critical amplitude values
def removeUnphyscialAmplitudes(amplitudes, rise_times, noise):
    criticalValues = findCriticalValues(amplitudes)
  
    for chan in amplitudes.dtype.names:
        
        indices = amplitudes[chan] > criticalValues[chan]*0.95
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        
        indices = amplitudes[chan] < noise[chan]*10
        amplitudes[chan][indices] = 0

    return amplitudes, rise_times, criticalValues


# Search for critical amplitude values
def findCriticalValues(data):
    
    channels = data.dtype.names
    criticalValues = dict()
    
    for chan in channels:
        criticalValues[chan] = 0
    
    for chan in channels:
        for entry in range(0,len(data)):
            if criticalValues[chan] < np.amax(data[chan][entry]):
                criticalValues[chan] = np.amax(data[chan][entry])


    return criticalValues


# Export dictionaries amplitude and risetime and list of channels in a .pkl file
def exportPulseInfo(amplitudes, rise_times, criticalValues):
    
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pulse_info_"+str(md.getRunNumber())+".pkl","wb") as output:
        
        pickle.dump(amplitudes,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(rise_times,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(criticalValues,output,pickle.HIGHEST_PROTOCOL)
