import numpy as np
import run_log_metadata as md

def pulseAnalysis(data, pedestal, noise):

    osc_limit = findOscilloscopeLimit(data)

    # Set the time scope to 0.1 ns
    defTimeScope()
    
    # Time in event when the pulse reaches maximum
    peak_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Pulse amplitude
    peak_value      =   np.zeros(len(data), dtype = data.dtype)
    
    # Rise time
    rise_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Time at 50% of the rising edge
    cfd           =   np.zeros(len(data), dtype = data.dtype)
    
    # Points above the threshold
    points           =   np.zeros(len(data), dtype = data.dtype)
    
    # Max sample of event given that there are points above the threshold
    max_sample      =   np.zeros(len(data), dtype = data.dtype)
    
    # Charge deposited fron the particle to the sensor
    charge          =   np.zeros(len(data), dtype = data.dtype)
    
    properties = [peak_time, peak_value, rise_time, cfd, points, max_sample, charge]

    for chan in data.dtype.names:
        for event in range(0, len(data)):
            
            variables = [data[chan][event], pedestal[chan], noise[chan], osc_limit[chan]]
            
            results = getPulseInfo(variables)
            
            for type in range(0, len(results)):
                properties[type][event][chan] = results[type]

    return properties


def getPulseInfo(variables):

    [data, pedestal, noise, osc_limit] = [i for i in variables]
    
    # Invert waveform data
    data = -data
    pedestal = -pedestal
    osc_limit = -osc_limit
    
    # Define threshold and sigma level
    N = 4
    
    # This number has been argumented as a combined plot between max sample
    # point and number of points above the threshold. See report.
    threshold_points = 5
    threshold = N * noise + pedestal
    
    if np.sum(data > threshold) >= threshold_points:
        
        points = calculatePoints(data, threshold)
        max_sample = np.amax(data)
        peak_value, peak_time = calculatePeakValue(data, pedestal, osc_limit)
        rise_time, cfd  = calculateRiseTime(data, pedestal)
        charge = calculateCharge(data, threshold, osc_limit)

        # Condition: if the time locations are not in synch, disregard those
        if peak_time == 0 or cfd == 0:
            
             peak_time = cfd = 0

        # Invert again to maintain the same shape
        return peak_time, -peak_value, rise_time, cfd, points, -max_sample, charge

    else:
        return np.zeros(7)


# Get Rise time
def calculateRiseTime(data, pedestal, graph=False):
    
    # Default values
    rise_time = np.zeros(1)
    cfd = np.zeros(1)
    linear_fit = np.zeros(2)
    linear_fit_indices = np.zeros(1)
    
    # Select points between 10 and 90 procent, before the max point
    linear_fit_bool = (data < np.amax(data)*0.9) & (data > np.amax(data)*0.1) & (np.nonzero(data) < np.argmax(data))[0]
    
    if np.sum(linear_fit_bool) > 0:
    
        linear_fit_indices = np.argwhere(linear_fit_bool).flatten()
        linear_fit_indices = getConsecutiveSeries(linear_fit_indices)
  
        # Require three points above threshold
        if len(linear_fit_indices) >= 3:

            x_values = linear_fit_indices * dt
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


def calculatePeakValue(data, pedestal, osc_limit, graph=False):

    # Default values
    peak_value = np.zeros(1)
    peak_time = np.zeros(1)
    poly_fit = np.zeros(3)

    # Select indices
    point_sep = 2
    arg_max = np.argmax(data)
    poly_fit_indices = np.arange(arg_max - point_sep, arg_max + point_sep + 1)
    
    # This is to ensure that the obtained value is in the entry window
    if 2 < arg_max < 999:
    
        poly_fit_data = data[poly_fit_indices]
        poly_fit = np.polyfit((poly_fit_indices * dt), poly_fit_data, 2)

        if poly_fit[0] < 0:
            
            peak_time = np.array([-poly_fit[1] / (2 * poly_fit[0])])
            peak_value = poly_fit[0] * np.power(peak_time, 2) + poly_fit[1] * peak_time + poly_fit[2] - pedestal

    

    # If the signal reaches the oscilloscope limit, take the maximum value instead and ignore the
    # time location, since it cannot be extracted with great precision

    if np.abs(np.amax(data) - osc_limit) < 0.005:

        peak_time = np.zeros(1)
        peak_value = np.amax(data) - pedestal


    if graph:
        return peak_value, peak_time, poly_fit
    
    else:
        return peak_value, peak_time


def calculateCharge(data, threshold, osc_limit):

    # transimpendence is the same for all sensors, except for W4-RD01, which is unknown
    transimpendence = 4700
    voltage_integral = np.trapz(data[data > threshold], dx = dt)*10**(-9)
    charge = voltage_integral / transimpendence
    
    return charge


def calculatePoints(data, threshold):

    points_threshold = np.argwhere(data > threshold).flatten()
    points_consecutive = getConsecutiveSeries(points_threshold)
    
    return len(points_consecutive)


def getConsecutiveSeries(data):

    group_points = group_consecutives(data)
    group_points_max = [np.amax(group) for group in group_points]
    max_arg_series = group_points[group_points_max.index(max(group_points_max))]
    
    return max_arg_series


# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

# Get maximum values for given channel and oscilloscope
def findOscilloscopeLimit(data):

    channels = data.dtype.names
    osc_limit = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        osc_limit[chan] = np.amin(np.concatenate(data[chan]))

    return osc_limit


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


def defTimeScope():
    global dt
    dt = 0.1

