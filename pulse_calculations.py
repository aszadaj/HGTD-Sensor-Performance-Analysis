import numpy as np
import data_management as dm
import sys
import metadata as md

def pulseAnalysis(data, pedestal, noise):

    channels = data.dtype.names
    
    # Calculate the maximum amplitude for which the oscilloscope reads out
    criticalValues = findCriticalValues(data)
    
    peak_times      =   np.zeros(len(data), dtype = data.dtype)
    peak_values     =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)


    for event in range(0, len(data)):
    
        for chan in channels:
            
            variables = [data[chan][event], pedestal[chan], noise[chan], chan, event, criticalValues[chan]]
            results = getAmplitudeAndRiseTime(variables)
            [peak_times[event][chan], peak_values[event][chan], rise_times[event][chan]] = [i for i in results]

    return peak_times, peak_values, rise_times


def getAmplitudeAndRiseTime (variables):

    [data, pedestal, noise, chan, event, criticalValue] = [i for i in variables]
    
    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1
    
    # Factor to regulate the threshold.
    N = 5
    
    # Relevant values from the pulse
    peak_time = 0
    peak_value = 0
    rise_time = 0
 
    # Set threshold, note data have negative pulse values
    threshold = -noise * N + pedestal
    threshold_indices = np.where(data < threshold)[0]
    
    try:

        # Restrict to finding the threshold and avoid values which have corrupted data
        if len(threshold_indices) > 0 and np.amin(data) != criticalValue:
            
            first_index = threshold_indices[0]
            last_index = np.argwhere(data < np.amin(data)*0.9)[0]
        
            # This is to adapt for the SiPM rise time distribution to look better
            # Does not affect other plots
            if chan == md.getChannelNameForSensor("SiPM-AFP"):
                last_index -= 2
           

            linear_fit_indices = np.arange(first_index, last_index)
            linear_fit_data = data[linear_fit_indices]
  
            # Data selection for polynomial fit
            point_difference = 3
            poly_fit_indices = np.arange(np.argmin(data) - point_difference, np.argmin(data) + point_difference+1)
            poly_fit_data = data[poly_fit_indices]
            
            # Previous setting, 2 points
            # Conditions on linear and 2nd degree fits
            if len(linear_fit_data) > 2:
                
                linear_fit = np.polyfit((linear_fit_indices * timeScope), linear_fit_data, 1)
                poly_fit = np.polyfit((poly_fit_indices * timeScope), poly_fit_data, 2)
                
                if linear_fit[0] < 0 and poly_fit[0] > 0:
                
                    # Reference point 50% of rise time, pedestal corrected
                    #peak_time = (0.5 * (np.amin(data) + pedestal) - linear_fit[1]) / linear_fit[0]
                    
                    # Reference point peak time location second method
                    peak_time = - poly_fit[1] / (2 * poly_fit[0])
                    
                    # Amplitude value with derivative of the fit taken as reference
                    peak_index = - poly_fit[1] / (2 * poly_fit[0])
                    peak_value = poly_fit[0] * np.power((peak_index), 2) + poly_fit[1] * peak_index + poly_fit[2] - pedestal
                    
                    # This method gives better results
                    rise_time = 0.8 * peak_value / linear_fit[0]

    except:

        print "Error caught"
        print sys.exc_info()[0]
        print event, chan, "\n"
        
        peak_value = 0
        peak_time = 0
        rise_time = 0

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
    
    peak_time = np.empty(0, dtype=results[0][0].dtype)
    peak_value  = np.empty(0, dtype=results[0][1].dtype)
    rise_time = np.empty(0, dtype=results[0][2].dtype)
    
    for index in range(0, len(results)):
    
        peak_time  = np.concatenate((peak_time,  results[index][0]), axis = 0)
        peak_value = np.concatenate((peak_value, results[index][1]), axis = 0)
        rise_time = np.concatenate((rise_time, results[index][2]), axis = 0)
    

    return [peak_time, peak_value, rise_time]


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


