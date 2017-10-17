import ROOT
import numpy as np
import root_numpy as rnm
import json

def main():
    end = raw_input ("Until which entry? (0-200 000) or m as max: ")
    dataFileName = "~/cernbox/oscilloscope_data/data_1504818689.tree.root"
    pulsePropertiesFileName = "pedestal_noise.json"
    
    data,channels = setUpData(dataFileName,end)
    
    pedestal,noise = importInfo(pulsePropertiesFileName)
    
    amplitudes = findAmplitudeForPulse(data,pedestal,noise)

def findAmplitudeForPulse(data,pedestal,noise):
    dt = 0.1
    amplitudes = dict()
    for chan in data.dtype.names:
        amplitudes[chan] = np.empty(0)
    eventNumber = 0
    for event in data:
        
        for chan in data.dtype.names:
            event[chan] = event[chan]*1000-pedestal[chan] # Convert from V to mV and remove the pedestal
            noise_limit = -25 # Set 25 mV limit on the noise oscillation curve
            amplitude_value = np.amin(event[chan])
            amplitude_index = np.argmin(event[chan])
            
            
            # How to extract the noise more exactly?
            # The STD for noise is about 2 up to 5 mV,
            # which is not in accordance with data (which is at least 5 mV)
            
            # Problem with defining where the pulse starts.
            # amplitude_places takes too many values which are irrelevant
            
            if  amplitude_value < noise_limit:
                amplitude_places = np.argwhere((event[chan][0:amplitude_index]>0.9*amplitude_value) & (event[chan][0:amplitude_index]<0.1*amplitude_value))
                print amplitude_places
                risetime = (np.amax(amplitude_places)-np.amin(amplitude_places))*dt
                print "event: " + str(eventNumber) + " channel: " + str(chan) + " risetime: " + str(risetime) + " min value: " + str(amplitude_value) + " index: " + str(amplitude_index)
                
              
                amplitudes[chan] = np.append(amplitudes[chan],amplitude_value)
                

        eventNumber+=1
    return amplitudes

def setUpData(dataFileName,end):
    
    data = ""
    
    if end == "m":
        data = rnm.root2array(dataFileName)
    else:
        data = rnm.root2array(dataFileName,stop=int(end))

    channels = data.dtype.names # gets names for the leafs in TTree file
    return data, channels

def importInfo(fileName):
    # load from file:
    with open(fileName, 'r') as f:
        try:
            data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            data = {}

    return data["p"],data["n"]

main()
