import numpy as np
import run_log_metadata as md
import data_management as dm

threshold_noise = 20 * 0.001
data_point_correction = 3


# Input is in negative values, but the calculation is in positive values!
# Dimensions used are U = [V], t = [ns], q = [C]
def getPulseCharacteristics(variables):

    [data, signal_limit_DUT, threshold_points] = [i for i in variables]
    
    # Invert waveform data
    data = -data
    signal_limit_DUT = -signal_limit_DUT
    
    # Define threshold and sigma level, this gives a 1% prob for a noise data sample to exceed the
    # noise level, see report
    N = 4.27
    noise, pedestal = calculateNoiseAndPedestal(data)
    threshold = N * noise + pedestal
    
    # points and max_sample are calculated without the threshold point condition
    # to analyze how many points are required
    points = calculatePoints(data, threshold)
    max_sample = np.amax(data[data > threshold]) if np.sum(data > threshold) != 0 else 0
    

    if points >= threshold_points:
        
        timeScope = 0.1
        peak_value, peak_time = calculatePeakValue(data, pedestal, signal_limit_DUT, timeScope)
        rise_time, cfd  = calculateRiseTime(data, pedestal, timeScope)
        charge = calculateCharge(data, threshold, timeScope)
        

        # Condition: if the time locations are not in synch, disregard those
        if peak_time == 0 or cfd == 0:

             peak_time = cfd = 0

        # Invert again to maintain the same shape
        return noise, -pedestal, -peak_value, rise_time, charge, cfd, peak_time, points, -max_sample

    else:
        return noise, -pedestal, 0, 0, 0, 0, 0, points, -max_sample


def calculateNoiseAndPedestal(data):

    # Select samples above threshold
    samples_bool = data > threshold_noise
    
    # If that is low, ignore the event (this is checked, happens for ~0.03 % of all events)
    if np.sum(samples_bool) > 0 and np.where(samples_bool)[0][0] <= data_point_correction:
    
        std = 0
        avg = 0
    
    # Select the first index exceeding the threshold.
    elif np.any(samples_bool):
    
        std = np.std(data[0:np.where(samples_bool)[0][0] - data_point_correction])
        avg = np.average(data[0:np.where(samples_bool)[0][0] - data_point_correction])
    

    # Otherwise, select the whole event
    else:
    
        std = np.std(data)
        avg = np.average(data)
    

    return std, avg



# Calculate the pulse amplitude value
def calculatePeakValue(data, pedestal, signal_limit_DUT, timeScope, graph=False):

    # Default values
    peak_value = 0
    peak_time = 0
    poly_fit = [0,0,0]

    # Select indices
    point_sep = 2
    arg_max = np.argmax(data)
    poly_fit_indices = np.arange(arg_max - point_sep, arg_max + point_sep + 1)
    
    # This is to ensure that the obtained value is in the entry window
    if 2 < arg_max < 999:
        
        print "peak_value", timeScope
        
        poly_fit_data = data[poly_fit_indices]
        poly_fit = np.polyfit((poly_fit_indices * timeScope), poly_fit_data, 2)

        if poly_fit[0] < 0:
            
            peak_time = np.array([-poly_fit[1] / (2 * poly_fit[0])])
            peak_value = poly_fit[0] * np.power(peak_time, 2) + poly_fit[1] * peak_time + poly_fit[2] - pedestal


    # If the signal reaches the oscilloscope limit, take the maximum value instead and ignore the
    # time location, since it cannot be extracted with great precision

    if np.abs(np.amax(data) - signal_limit_DUT) < 0.005:

        peak_time = np.zeros(1)
        peak_value = np.amax(data) - pedestal


    if graph:
        return peak_value, peak_time, poly_fit
    
    else:
        return peak_value, peak_time


# Get rise time
def calculateRiseTime(data, pedestal, timeScope, graph=False):
    
    print "rise time", timeScope
    
    # Default values
    rise_time = 0
    cfd = 0
    linear_fit = [0,0]
    linear_fit_indices = 0
    
    # Select points between 10 and 90 procent, before the max point
    linear_fit_bool = (data < np.amax(data)*0.9) & (data > np.amax(data)*0.1) & (np.nonzero(data) < np.argmax(data))[0]
    
    if np.sum(linear_fit_bool) > 0:
        
        linear_fit_indices = np.argwhere(linear_fit_bool).flatten()
        linear_fit_indices = getConsecutiveSeries(linear_fit_indices)
        
        # Require three points above threshold
        if len(linear_fit_indices) >= 3:
            
            x_values = linear_fit_indices * timeScope
            y_values = data[linear_fit_indices]
            
            linear_fit = np.polyfit(x_values, y_values, 1)
            
            if linear_fit[0] > 0:
                
                # Get rise time and CFD Z = 0.5 of the rising edge, pedestal corrected
                rise_time = 0.8 * (np.amax(data) - pedestal) / linear_fit[0]
                cfd = (0.5 * (np.amax(data) - pedestal) - linear_fit[1]) / linear_fit[0]

    if graph:
        return rise_time, cfd, linear_fit, linear_fit_indices
        
    else:
        return rise_time, cfd


# Calculate the charge over the threshold
def calculateCharge(data, threshold, timeScope):

    # transimpendence is the same for all sensors, except for W4-RD01, which is unknown
    transimpendence = 4700
    voltage_integral = np.trapz(data[data > threshold], dx = timeScope)*10**(-9)
    charge = voltage_integral / transimpendence
    
    return charge


# Calculate points above the threshold
def calculatePoints(data, threshold):

    points_threshold = np.argwhere(data > threshold).flatten()
    points_consecutive = getConsecutiveSeriesPoints(data, points_threshold)
    
    return len(points_consecutive)


# Select consecutive samples for a range of data set
def getConsecutiveSeriesPoints(data, points_threshold):
    
    if len(points_threshold) == 0:
        return []

    group_points = group_consecutives(points_threshold)
    group_points_max = [np.amax(data[group]) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


# Select consecutive samples which have the maximum height
def getConsecutiveSeries(data):
    
    if len(data) == 0:
        return []

    group_points = group_consecutives(data)
    group_points_max = [np.amax(group) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


# Group data which are consecutive
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)


# Get maximum values for given channel and oscilloscope
def getSignalLimit(data):

    signal_limit_DUT = np.empty(1, dtype=dm.getDTYPE())
    
    for chan in data.dtype.names:
        signal_limit_DUT[chan] = np.amin(np.concatenate(data[chan]))

    return signal_limit_DUT


# related to multiprocessing
def concatenateResults(results):

    variable_array = []

    for variable_index in range(0, len(results[0])):
        
        variable = np.empty(0, dtype=results[0][variable_index].dtype)
        
        for clutch in range(0, len(results)):
        
            variable  = np.concatenate((variable, results[clutch][variable_index]), axis = 0)
        
        variable_array.append(variable)
    
        del variable

    return variable_array


# These are set values for each sensor. These values are determined between a plot for:
# Combined plot between maximum sample value and point above the threshold. In this way
# one can cut away pulses which are treated as noise

def getThresholdSamples(chan):
    
    sensor = getSensor(chan)
    
    if sensor == "50D-GBGR2" or sensor == "W9-LGA35":
        number_samples = 5
    
    elif sensor == "SiPM-AFP" or sensor == "W4-RD01":
        number_samples = 50
    
    elif sensor == "W4-LG12" or sensor == "W4-S203" or sensor == "W4-S215" or sensor == "W4-S1061":
        number_samples = 10
    
    elif sensor == "W4-S204_6e14":
        number_samples = 3
    
    elif sensor == "W4-S1022":
        number_samples = 7
    
    
    return number_samples
