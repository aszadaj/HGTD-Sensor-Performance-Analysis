import numpy as np
import metadata as md
import data_management as dm
import warnings as wr
wr.simplefilter('ignore', np.RankWarning)
np.seterr(divide='ignore', invalid='ignore')

def pulseAnalysis(data, pedestal, noise, sigma):

    channels = data.dtype.names
    
    amplitudes      =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
    
    # DEBUG
    count = [0,0,0,0,0,0]
    
    criticalValues = findCriticalValues(data)

    for event in range(0,len(data)):
    
        for chan in channels:
            # Pedestal and noise are in mV whereas data is in V (and negative). Noise is a standard deviation, hence w/o minus.
            amplitudes[event][chan], rise_times[event][chan], count_new = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001, event, sigma, criticalValues[chan])
            # DEBUG
            for i in range(0, len(count_new)):
                count[i] += count_new[i]


    # DEBUG check how many pulses are disregarded
    if float(count[0])/(len(data)*8) > 0.0:
        print "linear condition", float(count[0])/(len(data)*8)
    if float(count[1])/(len(data)*8) > 0.0:
        print "crit", float(count[1])/(len(data)*8)
    if float(count[2])/(len(data)*8) > 0.0:
        print "curve condition", float(count[2])/(len(data)*8)
    if float(count[3])/(len(data)*8) > 0.0:
        print "linear poor fit", float(count[3])/(len(data)*8)
    if float(count[4])/(len(data)*8) > 0.0:
        print "2nd deg poor fit", float(count[3])/(len(data)*8)
    if float(count[5])/(len(data)*8) > 0.0:
        print "2nd deg poor fit try", float(count[3])/(len(data)*8)

    if sum(count) > 0:
        print "total", float(sum(count))/(len(data)*8), "\n"


    return amplitudes, rise_times


def getAmplitudeAndRiseTime (data_event, chan, pedestal, noise, eventNumber, sigma, criticalValue):

    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1
    
    max_amplitude = 0
    rise_time = 0
    
    # DEBUG
    count_linear = 0
    count_linear_poor_fit = 0
    count_critical = 0
    count_curve = 0
    count_2nd_deg_poor_fit = 0
    count_2nd_deg_poor_fit_catch = 0
    
    threshold = noise * sigma # This sets the condition for seeing a value above the noise.
    
    threshold_indices = np.where(data_event < - threshold) # Note, event is negative
    
    point_difference = 3 # This is to choose how many poins the second linear fit should be made

    # Check if there are points above the threshold
    if threshold_indices[0].size != 0:
        
        # Select the consecutive points, which have the highest peak
        group_points = group_consecutives(threshold_indices[0])
        group_points_amplitude = [np.amin(data_event[group]) for group in group_points]
        threshold_indices = group_points[group_points_amplitude.index(min(group_points_amplitude))]
        
        impulse_first = threshold_indices[0]
        impulse_last = np.argmin(data_event)
        
        # Linear fit - rise time
        impulse_data = data_event[impulse_first:impulse_last]
        impulse_min = np.amin(data_event)
        impulse_truth = (impulse_data > 0.9 * impulse_min ) & (impulse_data < 0.1 * impulse_min)
        impulse_indices = np.argwhere((impulse_data > 0.9 * impulse_min) & (impulse_data < 0.1 * impulse_min))

        # 2nd degree fit - maximal amplitude
        peak_first_index = impulse_last - point_difference
        peak_last_index = impulse_last + point_difference
        peak_indices = threshold_indices[np.where((threshold_indices >= peak_first_index) & (threshold_indices < peak_last_index))[0]]
        peak_data_points = data_event[peak_first_index:peak_last_index]
        
        # Corrupted events
        if np.amin(data_event) == criticalValue:
        
            count_critical = 1
            max_amplitude = 0
            rise_time = 0
        
        # Linear fit condition
        elif impulse_last - impulse_first < 3 or len(impulse_indices) == 0:
        
            count_linear = 1
            max_amplitude = 0
            rise_time = 0

        # Second degree fit condition
        elif len(peak_indices) != len(peak_data_points):
            count_curve = 1
            max_amplitude = 0
            rise_time = 0
            
            
        else:
            try:
                impulse_fit = np.polyfit(impulse_indices.flatten()*timeScope, impulse_data[impulse_truth].flatten(), 1)
                peak_fit = np.polyfit(peak_indices*timeScope, peak_data_points, 2)
                
                # If the linear fit is strange, omit it
                if impulse_fit[0] > -0.01 or np.isnan(impulse_fit[0]):
                
                    count_linear_poor_fit = 1
                    max_amplitude = 0
                    rise_time = 0

                # If the second degree fit is strange, omit it
                elif peak_fit[0] < 0.02:
                
                    count_2nd_deg_poor_fit = 1
                    max_amplitude = 0
                    rise_time = 0
                    
                else:
                
                    max_amplitude = peak_fit[0]*np.power(impulse_last*timeScope,2) + peak_fit[1]*impulse_last*timeScope + peak_fit[2]
                    rise_time = (impulse_min*0.8)/impulse_fit[0]
                    
            except ValueError:
                count_2nd_deg_poor_fit_catch = 1
                max_amplitude = 0
                rise_time = 0
            
        

            


    times = [count_linear, count_critical, count_curve, count_linear_poor_fit, count_2nd_deg_poor_fit, count_2nd_deg_poor_fit_catch]
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



