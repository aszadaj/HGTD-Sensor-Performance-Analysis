import numpy as np
import data_management as dm
import sys
import metadata as md

def pulseAnalysis(data, pedestal, noise):

    channels = data.dtype.names
    
    osc_limit = findOscilloscopeLimit(data)
    
    # Set the time scope to 0.1 ns
    defTimeScope()
    defCount()

    # Time in event when the pulse reaches maximum
    peak_times      =   np.zeros(len(data), dtype = data.dtype)
    
    # Pulse amplitude
    peak_values     =   np.zeros(len(data), dtype = data.dtype)
    
    # Rise time
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
    
    # Time at 50% of the rising edge
    cfd05           =   np.zeros(len(data), dtype = data.dtype)
    
    # POINT COUNT NOT ACTIVE
    # Number of consetutive points above 10%
    point_count           =   np.zeros(len(data), dtype = data.dtype)

    for chan in channels:
        for event in range(0, len(data)):
        
            variables = [data[chan][event], pedestal[chan], noise[chan], chan, event, osc_limit[chan]]
            
        
            results = getPulseInfo(variables)
            
            
            [peak_times[event][chan], peak_values[event][chan], rise_times[event][chan], cfd05[event][chan], point_count[event][chan]] = [i for i in results]
        
        #print getCountGroup()/len(data)*100, "%", chan
        
        #defCount()
    
    return peak_times, peak_values, rise_times, cfd05, point_count


def getPulseInfo(variables):

    [data, pedestal, noise, chan, event, osc_limit] = [i for i in variables]
    
    # Invert waveform data
    data = -data
    pedestal = -pedestal
    osc_limit = -osc_limit
    
    # Define threhsold and sigma level
    N = 4
    threshold = N * noise + pedestal
    
    if np.any(data > threshold):
    
        point_count = calculatePoints(data, pedestal, noise)
        peak_value, peak_time  = calculatePeakValue(data, pedestal, noise, osc_limit)
        
        if peak_value != 0:
            rise_time, cfd05  = calculateRiseTime(data, pedestal, noise)
            cfd05_v2 = calculateCFD05_V2(data, pedestal, noise)
        
        
        else:
            rise_time = 0
            cfd05 = 0
            point_count = 0
            cfd05_v2 = 0
        
        # Invert again to maintain the same shape
        return peak_time, -peak_value, rise_time, cfd05, point_count
    
    else:
        return 0, 0, 0, 0, 0


# Get Rise time
def calculateRiseTime(data, pedestal, noise, graph=False):
    
    # Default values
    rise_time = 0
    cfd05 = 0
    linear_fit = [0, 0]
    linear_fit_indices = [0]
    
    # Select points betweem 10 and 90 procent, before the max point and above noise and pedestal.
    linear_fit_bool = (data < np.amax(data)*0.9) & (data > np.amax(data)*0.1) & (data > (noise + pedestal)) & (np.nonzero(data) < np.argmax(data))[0]
    
    if np.sum(linear_fit_bool) > 0:
    
        linear_fit_indices = np.argwhere(linear_fit_bool).flatten()
        linear_fit_indices = getConsecutiveSeriesLinearFit(linear_fit_indices)
  
        # Require three points above threshold
        if len(linear_fit_indices) >= 3:

            x_values = linear_fit_indices * timeScope
            y_values = data[linear_fit_indices]
           
            linear_fit = np.polyfit(x_values, y_values, 1)
        
            if linear_fit[0] > 0:
                
                # Get rise time and CFD Z = 0.5 of the rising edge, pedestal corrected
                rise_time = 0.8 * (np.amax(data) + pedestal) / linear_fit[0]
                cfd05 = (0.5 * (np.amax(data) + pedestal) - linear_fit[1]) / linear_fit[0]

    if graph:
        return rise_time, cfd05, linear_fit, linear_fit_indices
    
    else:
        return rise_time, cfd05


def calculatePeakValue(data, pedestal, noise, osc_limit=350, graph=False):

    # Default values
    peak_value = 0
    peak_time = 0
    poly_fit = [0, 0, 0]

    # Select indices
    point_difference = 2
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    poly_fit_indices = np.arange(first_index, last_index+1)
    
    
    # This is to ensure that the obtained value is the entry window
    if 3 < np.argmax(data) < 999 and np.all(data[poly_fit_indices] > (noise + pedestal)):
    
        poly_fit_data = data[poly_fit_indices]
        poly_fit = np.polyfit((poly_fit_indices * timeScope), poly_fit_data, 2)

        if poly_fit[0] < 0:
            
            peak_time = -poly_fit[1]/(2 * poly_fit[0])
            peak_value = poly_fit[0] * np.power(peak_time, 2) + poly_fit[1] * peak_time + poly_fit[2] + pedestal
    

    # This is an extra check to prevent the second degree fit to fail and assign the maximum value instead
    if np.amax(data) == osc_limit:

        peak_time = 0
        peak_value = np.amax(data)


    if graph:
        return peak_value, peak_time, poly_fit
    
    else:
        return peak_value, peak_time


def calculatePoints(data, pedestal, noise):

    point_bool = (data > np.amax(data)*0.1) & (data > (noise + pedestal))
    if np.any(point_bool):
        points_condition = np.argwhere(point_bool).flatten()
        points_condition = getConsecutiveSeriesPointCalc(data, points_condition)
        return len(points_condition)
    else:
        return 0


def calculateCFD05_V2(data, pedestal, noise):
    
    # Default values
    cfd05_V2 = 0
    
    # Select points betweem 10 and 90 procent, before the max point and above noise and pedestal.
    linear_fit_bool = (data < np.amax(data)*0.9) & (data > np.amax(data)*0.1) & (data > (noise + pedestal)) & (np.nonzero(data) < np.argmax(data))[0]

    
    if np.sum(linear_fit_bool) > 0:
        
        linear_fit_indices = np.argwhere(linear_fit_bool).flatten()
        linear_fit_indices = getConsecutiveSeriesLinearFit(linear_fit_indices)
        
        value_05 = find_nearest(data[linear_fit_indices], (np.amax(data)+pedestal)*0.5)
        arg_05 = np.argwhere((data == value_05))[0]
    
        x_values = np.arange(arg_05-1,arg_05+2) * timeScope
        y_values = data[np.arange(arg_05-1,arg_05+2)]
       
        linear_fit = np.polyfit(x_values, y_values, 1)
      
        if linear_fit[0] > 0:
            cfd05_V2 = (0.5 * (np.amax(data) + pedestal) - linear_fit[1]) / linear_fit[0]


    return cfd05_V2

# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)



def getConsecutiveSeriesLinearFit(data):

    group_points = group_consecutives(data)
    group_points_max = [np.amax(group) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


def getConsecutiveSeriesPointCalc(data, points_condition):

    group_points = group_consecutives(points_condition)
    group_points_max = [np.amax(data[group]) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]


# Get maximum values for given channel and oscilloscope
def findOscilloscopeLimit(data):

    channels = data.dtype.names
    osc_limit = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        osc_limit[chan] = np.amin(np.concatenate(data[chan]))

    return osc_limit

# Function used to concatenate results from different clutches
# related to multiprocessing
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

def defCount():
    global count_group
    count_group = 0.0

def getCountGroup():

    return count_group


def defTimeScope():

    global timeScope
    timeScope = 0.1
    return timeScope


def increment_count_group():
    global count_group
    count_group = count_group + 1
