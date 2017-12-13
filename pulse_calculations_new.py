
import numpy as np

import metadata as md
import data_management as dm


# The code obtains amplitudes and rise time for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "rise_time".
def pulseAnalysis(data, pedestal, noise, sigma):

    channels = data.dtype.names
    
    amplitudes      =   np.zeros(len(data), dtype = data.dtype)
    rise_times      =   np.zeros(len(data), dtype = data.dtype)
    half_max_times  =   np.zeros(len(data), dtype = data.dtype)
    pulse_points    =   np.zeros(len(data), dtype = data.dtype)

    for event in range(0,len(data)):
    
        for chan in channels:
            # Pedestal and noise are in mV whereas data is in V (and negative). Noise is a standard deviation, hence w/o minus.
            amplitudes[event][chan], rise_times[event][chan], half_max_times[event][chan], pulse_points[event][chan] = getAmplitudeAndRiseTime(data[chan][event], chan, pedestal[chan]*-0.001, noise[chan]*0.001, event, sigma)

    return amplitudes, rise_times, half_max_times, pulse_points










# Calculate maximum amplitude value and rise time, if found.
# Function results zero values if
# 1. The pulse is not found
# 2. The pulse cannot be calculated, because of the conditions for polyfit (if for some reason there is a
#   'flat' function for the pulse

def getAmplitudeAndRiseTime (data_event, chan, pedestal, noise, eventNumber, sigma):
   
    # Time scope is the time difference between two recorded points
    # Assumption: for all events this value is the same.
    timeScope = 0.1

    pulse_amplitude = 0
    pulse_rise_time = 0
    pulse_half_maximum = 0
    pulse_data_points = -1
    
    # This sets the condition for seeing a value above the noise.
    threshold = noise * sigma - pedestal
    indices_condition = data_event < - threshold # Note, event is negative
    point_difference = 3
 
    # Indices condition should maybe be in consecutive order?

    if np.sum(indices_condition) > point_difference * 4:
    
    
    
        # 12.12.2017: implemention of better method of avoiding noises:
        # These lines, take out 1. groups of points in consecutive order
        # selects one which have the most points, which is the pulse
        # Defines these points, and only those, as the position of the pulse
        
        ############### NEW ####################
        
        group_points = group_consecutives(np.where(indices_condition)[0])
        group_points_length = [len(group) for group in group_points]
        pulse_indices = group_points[group_points_length.index(max(group_points_length))]
         # array which contain indices for the whole pulse, the most "relevant" one
        
        
        
        
        peak_index = np.argmin(data_event)
        
        # This defines how many points from the peak the fit should be considered
        peak_fit_first_index = peak_index - point_difference
        peak_fit_last_index = peak_index + point_difference
       
        peak_indices = pulse_indices[np.where((pulse_indices >= peak_fit_first_index) & (pulse_indices < peak_fit_last_index))[0]]
        
        peak_points = data_event[peak_fit_first_index:peak_fit_last_index]
    
        # Check why the polyfit fails
        if len(peak_indices) != len(peak_points):
            print "different"
            print peak_indices
            print peak_points
            print np.sum(indices_condition)
            print np.amin(data_event)
            print np.argmin(data_event)
            print group_points
            print len (group_points_length)
            print "event",eventNumber
            print chan, "\n"
        peak_fit = np.polyfit(peak_indices*timeScope, peak_points, 2)
       
        pulse_amplitude = peak_fit[0]*np.power(peak_index*timeScope,2) + peak_fit[1]*peak_index*timeScope+peak_fit[2]
        
      
        

        
        #########################################
        
        pulse_data_points = np.sum(indices_condition)
        
        # Investigate how many points you can remove
        pulse_first_index = np.where(indices_condition)[0][0] - 1 # Remove one point, just a convention
        pulse_last_index = np.argmin(data_event) # Peak
        pulse_amplitude = np.amin(data_event) - pedestal # Amplitude, pedestal corrected (usually few +-mV), not the best option, but
        
        amplitude_truth = (data_event[pulse_first_index:pulse_last_index] > 0.9*pulse_amplitude ) & (data_event[pulse_first_index:pulse_last_index] < 0.1*pulse_amplitude)
        amplitude_indices = np.argwhere((data_event[pulse_first_index:pulse_last_index] > 0.9*pulse_amplitude) & (data_event[pulse_first_index:pulse_last_index] < 0.1*pulse_amplitude))
        
        # Check if there are more than two points in the polyfit
        if len(amplitude_indices) > 4:
            
            # Make a linear fit, first degree
            # U = K*t + U_0
            [K, U_0] = np.polyfit(amplitude_indices.flatten()*timeScope, data_event[pulse_first_index:pulse_last_index][amplitude_truth].flatten(), 1)
       
            
            # This happens occasionally, if the
            if K == 0:
                print "WARNING polyfit gives a flat function! Batch",md.getRunNumber(),"data_event", eventNumber
                pulse_rise_time = 0
                pulse_amplitude = 0
                pulse_last_index = 0
            
            else:
                
                # Solution for first degree polynomial fit, y_amplitude = p[0]*x_time + p[1], where p is from polyfit
                # Rise time: time when the pulse is between 90% and 10% of the amplitude
                # 0.9*pulse_amplitude = K*pulse_rise_time_1 + U_0
                # 0.1*pulse_amplitude = K*pulse_rise_time_2 + U_0
                # -> delta pulse_rise_time = 0.8*pulse_amplitde/K
                
                pulse_rise_time = (pulse_amplitude*0.8)/K
                pulse_half_maximum = (pulse_amplitude*0.5)/K
        
        else:
            pulse_amplitude = 0
            pulse_last_index = 0

    return pulse_amplitude, pulse_rise_time, pulse_half_maximum, pulse_data_points



# Function which removes amplitudes which are in the range being critical amplitude values
# NOTE THIS FUNCTION HANDLES CONVERTED DATA (I.E. NEGATIVE TO POSITIVE VALUES AND IN mV)
# NOTE2 Here the amplitude values are pedestal corrected
def removeUnphyscialQuantities(results, noise, sigma):
   
    # There is a more beautiful fix, with nesting for loops, not important for now
    amplitudes      = np.empty(0,dtype=results[0][0].dtype)
    rise_times      = np.empty(0,dtype=results[0][1].dtype)
    half_max_times  = np.empty(0,dtype=results[0][2].dtype)
    pulse_points    = np.empty(0,dtype=results[0][3].dtype)
    
    for index in range(0, len(results)):
        amplitudes      = np.concatenate((amplitudes, results[index][0]), axis=0)
        rise_times      = np.concatenate((rise_times, results[index][1]), axis=0)
        half_max_times  = np.concatenate((half_max_times, results[index][2]), axis=0)
        pulse_points    = np.concatenate((pulse_points, results[index][3]), axis=0)

    criticalValues = findCriticalValues(amplitudes)
    
    deleted_amplitudes = np.zeros(1, dtype=amplitudes.dtype)
   
    for chan in amplitudes.dtype.names:
      
        indices = amplitudes[chan] == criticalValues[chan]
        
        amplitudes[chan][indices] = 0
        rise_times[chan][indices] = 0
        half_max_times[chan][indices] = 0
        
        deleted_amplitudes[chan] = np.sum(indices)

    return [convertData(amplitudes), rise_times, half_max_times, convertData(criticalValues), pulse_points, deleted_amplitudes]


# Search for critical amplitude values

def findCriticalValues(data):

    channels = data.dtype.names
    
    criticalValues = np.empty(1, dtype=data.dtype)
    
    for chan in channels:
        criticalValues[chan] = np.amin(data[chan])
    
    return criticalValues

# Convert to positive values in mV
def convertData(data):
  
    channels = data.dtype.names
  
    for chan in channels:
        data[chan] = np.multiply(data[chan],-1000)
    
    return data


def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)



