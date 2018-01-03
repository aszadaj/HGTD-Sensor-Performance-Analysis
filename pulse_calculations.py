import numpy as np
import metadata as md
import data_management as dm
import warnings as wr
wr.simplefilter('ignore', np.RankWarning)
np.seterr(divide='ignore', invalid='ignore')

def pulseAnalysis(data, pedestal, noise, sigma):

    count = 0

    channels = data.dtype.names
    
    peak_values     =   np.zeros(len(data), dtype = data.dtype)
    peak_times      =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
   
    criticalValues = findCriticalValues(data)

    for event in range(0,len(data)):
    
        for chan in channels:
        
            peak_values[event][chan], rise_times[event][chan], peak_times[event][chan], count = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001, event, sigma, criticalValues[chan] ,count)

    print float(count)/(len(data)*8)
    return peak_values, peak_times, rise_times


def getAmplitudeAndRiseTime (data, chan, pedestal, noise, event, sigma, criticalValue, count):

    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1
    
    # Relevant values from the pulse
    peak_value = 0
    peak_time = 0
    rise_time = 0
    
    # Set threshold, note data have negative pulse values
    threshold = noise * sigma - pedestal
    threshold_indices = np.where(data < -threshold)
    
    # Check if there are points above the threshold
    if threshold_indices[0].size > 4:
        
        # Consider consecutive points, with lowest peak value
        group_points = group_consecutives(threshold_indices[0])
        group_points_amplitude = [np.amin(data[group]) for group in group_points]
        threshold_indices = group_points[group_points_amplitude.index(min(group_points_amplitude))]
        
        # Data selection for linear fit
        impulse_indices = np.arange(threshold_indices[0], np.argmin(data)+1)
        impulse_data = data[impulse_indices]
        
        # Data selection for polynomial fit
        point_difference = 3
        peak_first_index = np.argmin(data) - point_difference
        peak_last_index = np.argmin(data) + point_difference
        peak_indices = np.arange(peak_first_index, peak_last_index+1)
        peak_data = data[peak_indices]
        
        # Corrupted event
        if np.amin(data) == criticalValue:
          
            count += 1
            
            peak_value = 0
            peak_time = 0
            rise_time = 0
        
        # Linear fit condition
        elif len(impulse_indices) < 3:

            count += 1
            
            peak_value = 0
            peak_time = 0
            rise_time = 0

        # Second degree fit condition
        elif data[peak_first_index] > threshold:
        
            count += 1
            
            peak_value = 0
            peak_time = 0
            rise_time = 0

        else:
        
            try:

                impulse_fit = np.polyfit(impulse_indices*timeScope, impulse_data, 1)
                peak_fit = np.polyfit(peak_indices*timeScope, peak_data, 2)
                
                # If the linear fit is strange, omit it
                if impulse_fit[0] > -0.01 or np.isnan(impulse_fit[0]):
            
                    count += 1
            
                    peak_value = 0
                    peak_time = 0
                    rise_time = 0

                # If the second degree fit is strange, omit it
                elif peak_fit[0] < 0.02:
        
                    count += 1
            
                    peak_value = 0
                    peak_time = 0
                    rise_time = 0
                    
                else:
                
                    peak_value = peak_fit[0]*np.power(np.argmin(data)*timeScope,2) + peak_fit[1]*np.argmin(data)*timeScope + peak_fit[2] - pedestal
                    
                    # Derivative polynomial fit
                    peak_time = -peak_fit[1]/(2*peak_fit[0])
                    
                    rise_time = (np.amin(data)-pedestal)*0.8/impulse_fit[0]
        
        
            except ValueError:
            
                count += 1
            
                peak_value = 0
                peak_time = 0
                rise_time = 0

    elif 0 < threshold_indices[0].size <= 4:
        count += 1
    
    return peak_value, rise_time, peak_time, count


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
    
    peak_values = np.empty(0, dtype=results[0][0].dtype)
    peak_times  = np.empty(0, dtype=results[0][1].dtype)
    rise_times = np.empty(0, dtype=results[0][2].dtype)
    
    for index in range(0, len(results)):
        peak_values = np.concatenate((peak_values, results[index][0]), axis = 0)
        peak_times  = np.concatenate((peak_times,  results[index][1]), axis = 0)
        rise_times = np.concatenate((rise_times, results[index][2]), axis = 0)
    
    for chan in channels:
        peak_values[chan] = np.multiply(peak_values[chan], -1000)
    
    return [peak_values, peak_times, rise_times]


# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)




