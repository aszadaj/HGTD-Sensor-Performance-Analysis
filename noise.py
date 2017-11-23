import pickle
import numpy as np

import metadata as md

# Calculate the noise for all channels
def noiseAnalysis(data):
    
    channels = data.dtype.names
    
    noise_average = np.zeros(len(data), dtype = data.dtype)
    noise_std = np.zeros(len(data), dtype = data.dtype)
    
    for event in range(0,len(data)):
        for chan in channels:
            
            pulse_compatible_samples = data[event][chan] < -25*0.001
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            noise_average[event][chan] = np.average(data[event][chan][0:max_index])
            noise_std[event][chan] = np.std(data[event][chan][0:max_index])

    return noise_average, noise_std


# Export noise data in a pickle file
def exportNoiseInfo(pedestal, noise, noise_average, noise_std):

    exportNoiseData(noise_average, noise_std)
    exportNoiseMean(pedestal, noise)


# Export pedestal info (noise analysis)
def exportNoiseData(noise_average, noise_std):

    fileName = md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_data/noise_data_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"wb") as output:
        pickle.dump(noise_average,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(noise_std,output,pickle.HIGHEST_PROTOCOL)


# Export pedestal info (noise analysis)
def exportNoiseMean(pedestal, noise):

    fileName = md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_mean/noise_mean_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"wb") as output:
        pickle.dump(pedestal,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(noise,output,pickle.HIGHEST_PROTOCOL)


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importNoiseData():
    
    fileName = md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_data/noise_data_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"rb") as input:
        noise_average = pickle.load(input)
        noise_std = pickle.load(input)

    return noise_average, noise_std


# Import noise mean values, i.e. noise and pedestal values
def importNoiseMean():
    
    fileName = md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_mean/noise_mean_"+str(md.getRunNumber())+".pkl"
    
    with open(fileName,"rb") as input:
        pedestal = pickle.load(input)
        noise = pickle.load(input)

    return pedestal, noise


# Calculates pedestal and noise mean values per channel for all entries
def getPedestalAndNoisePerChannel(noise_average, noise_std):
    
    pedestal = dict()
    noise = dict()

    for chan in noise_average.dtype.names:
        pedestal[chan] = np.mean(noise_average[chan])
        noise[chan] = np.mean(noise_std[chan])
    
    return pedestal, noise


