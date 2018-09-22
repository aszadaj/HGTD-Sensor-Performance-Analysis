import numpy as np

# Here the input is in negative values
def findNoiseAverageAndStd(data):
   
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    for event in range(0, len(data)):
    
        for chan in data.dtype.names:
            
            noise_average[event][chan], noise_std[event][chan] = calculateNoiseAndPedestal(data[event][chan])

            if np.isnan(noise_average[event][chan]) or np.isnan(noise_average[event][chan]):
            
                noise_average[event][chan]  = 0
                noise_std[event][chan]      = 0


    return noise_average, noise_std

# Here the input is in negative values
def calculateNoiseAndPedestal(data):

    # Consider points until a pulse
    threshold = -20 * 0.001 # mV
    
    data_point_correction = 3
    
    # Take out points which are below the noise level
    pulse_samples_bool = data < threshold
    
    # Select the "last index" which defines the range of the noise selection
    max_index = np.where(pulse_samples_bool)[0][0] - data_point_correction if len(np.where(pulse_samples_bool)[0] ) else 1002
 
    return np.average(data[0:max_index]), np.std(data[0:max_index])



def concatenateResults(results):

    channels = results[0][0].dtype.names
    
    noise_average   = np.empty(0, dtype=results[0][0].dtype)
    noise_std       = np.empty(0, dtype=results[0][1].dtype)
    
    for index in range(0, len(results)):
        noise_average   = np.concatenate((noise_average, results[index][0]), axis = 0)
        noise_std       = np.concatenate((noise_std, results[index][1]), axis = 0)
    
    return [noise_average, noise_std]

