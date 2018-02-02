import numpy as np
import metadata as md
import data_management as dm
import warnings as wr
import sys

#wr.simplefilter('ignore', np.RankWarning)
#np.seterr(divide='ignore', invalid='ignore')

def pulseAnalysis(data, pedestal, noise):

    channels = data.dtype.names
    
    peak_times      =   np.zeros(len(data), dtype = data.dtype)
    peak_values     =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)

    criticalValues = findCriticalValues(data)

    for event in range(0,len(data)):
    
        for chan in channels:
        
            peak_times[event][chan], peak_values[event][chan], rise_times[event][chan] = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan], noise[chan], event, criticalValues[chan])

    return peak_times, peak_values, rise_times


def getAmplitudeAndRiseTime (data, chan, pedestal, noise, event, criticalValue):

    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1
    
    # Relevant values from the pulse
    peak_value = 0
    peak_time = 0
    rise_time = 0
    
    # Set threshold, note data have negative pulse values
    threshold = noise * md.sigma - pedestal
    threshold_indices = np.where(data < -threshold)
    
    try:
    
        if threshold_indices[0].size != 0:
            
            # Consider consecutive points, with lowest peak value
            group_points = group_consecutives(threshold_indices[0])
            group_points_amplitude = [np.amin(data[group]) for group in group_points]
            threshold_indices = group_points[group_points_amplitude.index(min(group_points_amplitude))]
            
            if len(threshold_indices) > 6:
                
                impulse_indices = np.arange(threshold_indices[0], np.argmin(data)+1)
                impulse_data = data[impulse_indices]
                
                # Data selection for polynomial fit
                point_difference = 2
                peak_first_index = np.argmin(data) - point_difference
                peak_last_index = np.argmin(data) + point_difference
                peak_indices = np.arange(peak_first_index, peak_last_index+1)
                peak_data = data[peak_indices]
                
                # Corrupted event
                if np.amin(data) != criticalValue and len(impulse_indices) > 4:
                
                    impulse_fit = np.polyfit(impulse_indices*timeScope, impulse_data, 1)
                    peak_fit = np.polyfit(peak_indices*timeScope, peak_data, 2)
                    
                    if impulse_fit[0] < 0 and peak_fit[0] > 0.05:
                
                        peak_value = peak_fit[0]*np.power(np.argmin(data)*timeScope,2) + peak_fit[1]*np.argmin(data)*timeScope + peak_fit[2] - pedestal
                        
                        # Derivative polynomial fit
                        peak_time = -peak_fit[1]/(2*peak_fit[0])
                     
                        rise_time = (np.amin(data)-pedestal)*0.8/impulse_fit[0]

    except:
    
        print "Error caught"
        print sys.exc_info()[0]
        print event, chan, "\n"
    
    return peak_time, peak_value, rise_time


# Search for critical amplitude values

def findCriticalValues(data):

    channels = data.dtype.names
    criticalValues = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        criticalValues[chan] = np.amin(np.concatenate(data[chan]))

    return criticalValues


# Convert to positive values in mV
def concatenateResults(results):

    channels = results[0][0].dtype.names
    
    peak_times = np.empty(0, dtype=results[0][0].dtype)
    peak_values  = np.empty(0, dtype=results[0][1].dtype)
    rise_times = np.empty(0, dtype=results[0][2].dtype)
    
    for index in range(0, len(results)):
    
        peak_times  = np.concatenate((peak_times,  results[index][0]), axis = 0)
        peak_values = np.concatenate((peak_values, results[index][1]), axis = 0)
        rise_times = np.concatenate((rise_times, results[index][2]), axis = 0)
    

    return [peak_times, peak_values, rise_times]


def getPedestalAndNoise(noise_average, noise_std):

    pedestal = np.empty(0)
    noise = np.empty(0)

    for chan in noise_average.dtype.names:
        
        if pedestal.size == 0:

            pedestal = np.empty(1, dtype=noise_average.dtype)
            noise = np.empty(1, dtype=noise_std.dtype)
        
        pedestal[chan] = np.average(noise_average[chan])
        noise[chan] = np.average(noise_std[chan])
        

    return pedestal, noise

# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)


