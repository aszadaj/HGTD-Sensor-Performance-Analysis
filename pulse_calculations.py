import numpy as np

timeScope = 0.1
threshold_noise = 20 * 0.001
data_point_correction = 3


# Input is in negative values, but the calculation is in positive values!
# Dimensions used are U = [V], t = [ns], q = [C]
def getPulseCharacteristics(data, signal_limit, threshold_points):
    
    # Invert waveform data
    data = -data
    signal_limit = -signal_limit
    
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
        
        pulse_amplitude, peak_time = calculatePeakValue(data, pedestal, signal_limit)
        rise_time, cfd  = calculateRiseTime(data, pedestal)
        charge = calculateCharge(data, threshold)
        

        # Condition: if the time locations are not in synch, disregard those
        if peak_time == 0 or cfd == 0:

             peak_time = cfd = 0

        # Invert again to maintain the same shape
        return noise, -pedestal, -pulse_amplitude, rise_time, charge, cfd, peak_time, points, -max_sample

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
def calculatePeakValue(data, pedestal, signal_limit, graph=False):

    # Default values
    pulse_amplitude = 0
    peak_time = 0
    second_deg_fit = [0,0,0]

    # Select indices
    point_sep = 2
    arg_max = np.argmax(data)
    poly_fit_indices = np.arange(arg_max - point_sep, arg_max + point_sep + 1)
    
    # This is to ensure that the obtained value is in the entry window
    if 2 < arg_max < 999:
        poly_fit_data = data[poly_fit_indices]
        
        second_deg_fit = np.polyfit(poly_fit_indices * timeScope, poly_fit_data, 2)

        if second_deg_fit[0] < 0:
            
            peak_time = np.array([-second_deg_fit[1] / (2 * second_deg_fit[0])])
            pulse_amplitude = second_deg_fit[0] * np.power(peak_time, 2) + second_deg_fit[1] * peak_time + second_deg_fit[2] - pedestal


    # If the signal reaches the oscilloscope limit, take the maximum value instead and ignore the
    # time location, since it cannot be extracted with great precision

    if np.abs(np.amax(data) - signal_limit) < 0.005:

        peak_time = np.zeros(1)
        pulse_amplitude = np.amax(data) - pedestal


    if graph:
        return pulse_amplitude, peak_time, second_deg_fit
    
    else:
        return pulse_amplitude, peak_time


# Get rise time
def calculateRiseTime(data, pedestal, graph=False):
    
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
def calculateCharge(data, threshold):

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


# related to multiprocessing
def concatenateResults(results):

    variable_array = []

    for variable_index in range(0, len(results[0])):
        
        variable = np.empty(0, dtype=results[0][variable_index].dtype)
        
        for group in range(0, len(results)):
        
            variable  = np.concatenate((variable, results[group][variable_index]), axis = 0)
        
        variable_array.append(variable)
    
        del variable

    return variable_array

