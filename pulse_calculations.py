import numpy as np
import metadata as md
import data_management as dm

def pulseAnalysis(data, pedestal, noise, sigma):

    channels = data.dtype.names
    
    amplitudes      =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
    times = [0,0,0,0,0]
    
    # This function lists max amplitude values for each channel among all data points
    
    criticalValues = findCriticalValues(data)

    for event in range(0,len(data)):
    
        for chan in channels:
            # Pedestal and noise are in mV whereas data is in V (and negative). Noise is a standard deviation, hence w/o minus.
            amplitudes[event][chan], rise_times[event][chan], times_new = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001, event, sigma, criticalValues[chan])
            
            for i in range(0, len(times)):
                times[i] += times_new[i]

     # DEBUG
    if times[0] > 0:
        print "large", times[0]
    if times[1] > 0:
        print "small", times[1]
    if times[2] > 0:
        print "crit", times[2]
    if times[3] > 0:
        print "lin fail", times[3]
    if times[4] > 0:
        print "2nd fit fail", times[4]

    

    return amplitudes, rise_times


def getAmplitudeAndRiseTime (data_event, chan, pedestal, noise, eventNumber, sigma, criticalValue):

    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1
    
    max_amplitude = 0
    rise_time = 0
    
    # DEBUG
    count_small = 0
    count_large = 0
    count_crit = 0
    count_lin_fail = 0
    count_2fit_fail = 0
    
    threshold = noise * sigma # This sets the condition for seeing a value above the noise.
    
    threshold_indices = np.where(data_event < - threshold) # Note, event is negative
    
    point_difference = 2 # This is to choose how many poins the second linear fit should be made

    # Check if there are points above the threshold
    if threshold_indices[0].size != 0:
        
        # Select the consecutive points, which have the highest peak
        group_points = group_consecutives(threshold_indices[0])
        group_points_amplitude = [np.amin(data_event[group]) for group in group_points]
        threshold_indices = group_points[group_points_amplitude.index(min(group_points_amplitude))]
        
        # With this peak, check if it is high enough and cointain sufficient amount of points
        if -np.amin(data_event) > 40*0.001 and len(threshold_indices) > point_difference * 2:
        
            # Check if the data of the event is "corrupted" meaning that it reaches a critical amplitude value

            if np.amin(data_event) == criticalValue:
                count_crit = 1
                max_amplitude = 0
                rise_time = 0
            
            else:
            
                # Create linear fit, to calculate rise time
                pulse_first_index = threshold_indices[0]
                pulse_last_index = np.argmin(data_event)
                max_amplitude = np.amin(data_event)
                amplitude_truth = (data_event[pulse_first_index:pulse_last_index] > 0.9*max_amplitude ) & (data_event[pulse_first_index:pulse_last_index] < 0.1*max_amplitude)
                amplitude_indices = np.argwhere((data_event[pulse_first_index:pulse_last_index] > 0.9*max_amplitude) & (data_event[pulse_first_index:pulse_last_index] < 0.1*max_amplitude))
                
                # If the linear fit fails, exit the calculation
                if len(amplitude_indices) == 0:
                    count_lin_fail = 1
                    print "linear fail", eventNumber, chan
                    max_amplitude = 0
                    rise_time = 0
                    times = [0,0,0,0,0]
                    return max_amplitude, rise_time, times
                
                
                linear_fit = np.polyfit(amplitude_indices.flatten()*timeScope, data_event[pulse_first_index:pulse_last_index][amplitude_truth].flatten(), 1)
              
                ## Get rise time for pulse ##
                rise_time = (max_amplitude*0.8)/linear_fit[0]
                
                
                # Create 2nd degree fit on the peak, for a reference point and have a better amplitude value
                peak_fit_first_index = pulse_last_index - point_difference
                peak_fit_last_index = pulse_last_index + point_difference
                peak_indices = threshold_indices[np.where((threshold_indices >= peak_fit_first_index) & (threshold_indices < peak_fit_last_index))[0]]
                peak_data_points = data_event[peak_fit_first_index:peak_fit_last_index]
                
                # If the second degree linear fit fails, use the old max_amplitude value
                if len(peak_indices) != len(peak_data_points):
                    count_2fit_fail = 1
                    peak_fit = np.polyfit(peak_indices*timeScope, peak_data_points, 2)
                    ## Get max amplitude value for the pulse ##
                    max_amplitude = peak_fit[0]*np.power(pulse_last_index*timeScope,2) + peak_fit[1]*pulse_last_index*timeScope + peak_fit[2]
    
    
        # If we have a small amplitude value, check if there are sufficient amount of points
        elif len(threshold_indices) > 5:
        
            # Here an approximation of the rise time is given
            max_amplitude = np.amin(data_event)
            rise_time = (np.argmin(data_event) - threshold_indices[0])*timeScope
            
            #print "small", chan, eventNumber, np.argmin(data_event), threshold_indices[0], max_amplitude, rise_time
        
        # Otherwise, disregard the pulse
        else:
            count_small = 1
            max_amplitude = 0
            rise_time = 0

    times = [count_large, count_small, count_crit, count_lin_fail, count_2fit_fail]
    return max_amplitude, rise_time, times


# Search for critical amplitude values

def findCriticalValues(data):

    channels = data.dtype.names
    criticalValues = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        criticalValues[chan] = np.amin(np.concatenate(data[chan]))

    return criticalValues


# Convert to positive values in mV
def convertPulseData(results):

    channels = results[0][0].dtype.names
    
    amplitudes = np.empty(0, dtype=results[0][0].dtype)
    rise_times = np.empty(0, dtype=results[0][1].dtype)
    
    for index in range(0, len(results)):
        amplitudes = np.concatenate((amplitudes, results[index][0]), axis = 0)
        rise_times = np.concatenate((rise_times, results[index][1]), axis = 0)
    
    for chan in channels:
        amplitudes[chan] = np.multiply(amplitudes[chan], -1000)
    
    return [amplitudes, rise_times]

# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)



