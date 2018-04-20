import numpy as np

def findNoiseAverageAndStd(data):
   
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    

    for event in range(0, len(data)):
    
        for chan in channels:
            
            # Consider points until a pulse
            pulse_limit = -20 * 0.001 # mV
            
            data_point_correction = 3
            
            # Take out points which are below the noise level
            pulse_compatible_samples = data[event][chan] < pulse_limit
            
            # Select the "last index" which defines the range of the noise selection
            max_index = np.where(pulse_compatible_samples)[0][0] - data_point_correction if len(np.where(pulse_compatible_samples)[0] ) else 1002
            
            noise_average[event][chan]  = np.average(data[event][chan][0:max_index])
            noise_std[event][chan]      = np.std(data[event][chan][0:max_index])
            
            if np.isnan(noise_average[event][chan]) or np.isnan(noise_average[event][chan]):
            
                noise_average[event][chan]  = 0
                noise_std[event][chan]      = 0


    return noise_average, noise_std


def concatenateResults(results):

    channels = results[0][0].dtype.names
    
    noise_average   = np.empty(0, dtype=results[0][0].dtype)
    noise_std       = np.empty(0, dtype=results[0][1].dtype)
    
    for index in range(0, len(results)):
        noise_average   = np.concatenate((noise_average, results[index][0]), axis = 0)
        noise_std       = np.concatenate((noise_std, results[index][1]), axis = 0)
    
    return [noise_average, noise_std]

