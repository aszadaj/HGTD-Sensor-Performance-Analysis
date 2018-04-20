import numpy as np
import data_management as dm
import sys
import metadata as md

def pulseAnalysis(data, pedestal, noise):

    channels = data.dtype.names
    
    osc_limit = findOscilloscopeLimit(data)
    
    # Time in event when the pulse reaches maximum
    peak_times      =   np.zeros(len(data), dtype = data.dtype)
    
    # Pulse amplitude
    peak_values     =   np.zeros(len(data), dtype = data.dtype)
    
    # Rise time
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
    
    # Time at 50% of the rising edge
    cfd05           =   np.zeros(len(data), dtype = data.dtype)
    
    # Number of consetutive points above 10%
    point_count           =   np.zeros(len(data), dtype = data.dtype)

    for chan in channels:
        count = 0.0
        for event in range(0, len(data)):
        
            variables = [data[chan][event], pedestal[chan], noise[chan], chan, event, osc_limit[chan], count]
            results = getAmplitudeAndRiseTime(variables)
            [peak_times[event][chan], peak_values[event][chan], rise_times[event][chan], cfd05[event][chan], count, point_count[event][chan]] = [i for i in results]

        #print count/len(data)*100, "%", md.getNameOfSensor(chan)
    return peak_times, peak_values, rise_times, cfd05, point_count


def getAmplitudeAndRiseTime(variables):

    [data, pedestal, noise, chan, event, osc_limit, count] = [i for i in variables]
    
    # Time span between two recorded points, in nanoseconds
    timeScope = 0.1
    
    # Factor to regulate the threshold.
    N = 4
    
    # Default values
    peak_time = 0
    peak_value = 0
    rise_time = 0
    cfd05 = 0
    point_count = 0 # Count the number of points above threshold
 
    # Note: Pedestal is based on negative values from the oscilloscope
    # Noise is always positive, needs to be corrected
    threshold = N * (-noise) + pedestal
    threshold_indices = np.where(data < threshold)[0]
    
    if len(threshold_indices) > 0:
        group_points = group_consecutives(threshold_indices)
        group_points_amplitude = [np.amin(data[group]) for group in group_points]
        threshold_indices = group_points[group_points_amplitude.index(min(group_points_amplitude))]

        # Implement collection of points above 10%
        if len(threshold_indices) > 0:

            data_selection = np.where(data < np.amin(data)*0.1)[0]

            group_points = group_consecutives(data_selection)
            group_points_amplitude = [np.amin(data[group]) for group in group_points]
            data_selection_consecutive = group_points[group_points_amplitude.index(min(group_points_amplitude))]

            point_count = len(data_selection_consecutive)
        
    try:

        if len(threshold_indices) > 4:

            # Data selection for linear fit on the rising edge of the pulse
            first_index = threshold_indices[0] - 1
            last_index = threshold_indices[(data[threshold_indices] > np.amin(data)*0.9) & ( threshold_indices < np.argmin(data))][-1]
            linear_fit_indices = np.arange(first_index, last_index+1)
            linear_fit_data = data[linear_fit_indices]
        
            # Data selection for polynomial fit
            point_difference = 2
            first_index = np.argmin(data) - point_difference
            last_index = np.argmin(data) + point_difference
            poly_fit_indices = np.arange(first_index, last_index+1)
            poly_fit_data = data[poly_fit_indices]
            
            # Conditions on linear and 2nd degree fits
            if len(linear_fit_data) > 2:
        
                linear_fit = np.polyfit((linear_fit_indices * timeScope), linear_fit_data, 1)
                poly_fit = np.polyfit((poly_fit_indices * timeScope), poly_fit_data, 2)
                
                if linear_fit[0] < 0 and poly_fit[0] > 0:
                    
                    cfd05 = (0.5*(np.amin(data) + pedestal) - linear_fit[1]) / linear_fit[0]
                   
                    peak_time = -poly_fit[1]/(2 * poly_fit[0])
                    
                    peak_value = poly_fit[0] * np.power(peak_time, 2) + poly_fit[1] * peak_time + poly_fit[2] + pedestal
                    
                    rise_time = 0.8 * peak_value / linear_fit[0]
            

                # This is a extra check to prevent the second degree fit to fail and assign the maximum value instead
                if np.amin(data) == osc_limit:

                    peak_time = 0
                    peak_value = np.amin(data)
                    rise_time = 0.8 * peak_value / linear_fit[0]



    except:

#        print "Error caught"
#        print sys.exc_info()[0]
#        print event, chan, md.getNameOfSensor(chan), "\n"
        count += 1

        peak_value = 0
        peak_time = 0
        rise_time = 0
        cfd05 = 0

    return peak_time, peak_value, rise_time, cfd05, count, point_count


# Get maximum values for given channel and oscilloscope
def findOscilloscopeLimit(data):

    channels = data.dtype.names
    osc_limit = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        osc_limit[chan] = np.amin(np.concatenate(data[chan]))

    return osc_limit


# Convert to positive values in mV
def concatenateResults(results):

    channels = results[0][0].dtype.names
    
    peak_time = np.empty(0, dtype=results[0][0].dtype)
    peak_value  = np.empty(0, dtype=results[0][1].dtype)
    rise_time = np.empty(0, dtype=results[0][2].dtype)
    cfd05 = np.empty(0, dtype=results[0][3].dtype)
    point_count = np.empty(0, dtype=results[0][4].dtype)
    
    for index in range(0, len(results)):
    
        peak_time  = np.concatenate((peak_time,  results[index][0]), axis = 0)
        peak_value = np.concatenate((peak_value, results[index][1]), axis = 0)
        rise_time = np.concatenate((rise_time, results[index][2]), axis = 0)
        cfd05 = np.concatenate((cfd05, results[index][3]), axis = 0)
        
        point_count = np.concatenate((point_count, results[index][4]), axis = 0)
    

    return [peak_time, peak_value, rise_time, cfd05, point_count]



# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)


