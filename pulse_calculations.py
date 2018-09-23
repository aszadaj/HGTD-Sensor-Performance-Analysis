import numpy as np
import run_log_metadata as md
import data_management as dm

def pulseAnalysis(data, noise, pedestal):
    
    signal_limit_DUT = getSignalLimit(data)

    # Set the time scope to 0.1 ns
    defTimeScope()
    
    # Pulse amplitude
    peak_value      =   np.zeros(len(data), dtype = data.dtype)
    
    # Rise time
    rise_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Charge deposited fron the particle to the sensor
    charge          =   np.zeros(len(data), dtype = data.dtype)
    
    # Time at 50% of the rising edge
    cfd           =   np.zeros(len(data), dtype = data.dtype)
    
    # Time in event when the pulse reaches maximum
    peak_time       =   np.zeros(len(data), dtype = data.dtype)
    
    # Points above the threshold
    points           =   np.zeros(len(data), dtype = data.dtype)
    
    # Max sample of event given that there are points above the threshold
    max_sample      =   np.zeros(len(data), dtype = data.dtype)
    
    properties = [peak_value, rise_time, charge, cfd, peak_time, points, max_sample]

    for chan in data.dtype.names:
        
        for event in range(0, len(data)):
            
            variables = [data[chan][event], noise[chan], pedestal[chan], signal_limit_DUT[chan], md.getThresholdSamples(chan), chan]
            
            results = getPulseCharacteristics(variables)
            
            for type in range(0, len(results)):
                properties[type][event][chan] = results[type]

    
    return properties

# Input is in negative values, but the calculation is in positive values!
# Dimensions used are U = [V], t = [ns], q = [C]
def getPulseCharacteristics(variables):

    [data, noise, pedestal, signal_limit_DUT, threshold_points, chan] = [i for i in variables]
    
    # Invert waveform data
    data = -data
    pedestal = -pedestal
    signal_limit_DUT = -signal_limit_DUT
    
    # Define threshold and sigma level, this gives a 1% prob for a noise data sample to exceed the
    # noise level, see report
    N = 4.27
    threshold = N * noise + pedestal

    
    # points and max_sample are calculated without the threshold point condition
    # to analyze how many points are required
    points = calculatePoints(data, threshold)
    max_sample = np.amax(data[data > threshold]) if np.sum(data > threshold) != 0 else 0


    if points >= threshold_points:

        peak_value, peak_time = calculatePeakValue(data, pedestal, signal_limit_DUT)
        rise_time, cfd  = calculateRiseTime(data, pedestal)
        charge = calculateCharge(data, threshold)

        # Condition: if the time locations are not in synch, disregard those
        if peak_time == 0 or cfd == 0:

             peak_time = cfd = 0

        # Invert again to maintain the same shape
        return -peak_value, rise_time, charge, cfd, peak_time, points, -max_sample

    else:
        return 0, 0, 0, 0, 0, points, -max_sample


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

# Calculate the pulse amplitude value
def calculatePeakValue(data, pedestal, signal_limit_DUT, graph=False):

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
    
        poly_fit_data = data[poly_fit_indices]
        poly_fit = np.polyfit((poly_fit_indices * dt), poly_fit_data, 2)

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


def calculateCharge(data, threshold):

    # transimpendence is the same for all sensors, except for W4-RD01, which is unknown
    transimpendence = 4700
    voltage_integral = np.trapz(data[data > threshold], dx = dt)*10**(-9)
    charge = voltage_integral / transimpendence
    
    return charge


def calculatePoints(data, threshold):

    points_threshold = np.argwhere(data > threshold).flatten()
    points_consecutive = getConsecutiveSeriesPoints(data, points_threshold)
    
    return len(points_consecutive)


# Select consecutive samples which have the maximum height
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


# Group each consequential numbers in each separate list
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


def defTimeScope():
    global dt
    dt = 0.1

