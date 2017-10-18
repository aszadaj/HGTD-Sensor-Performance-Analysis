import ROOT
import numpy as np
import root_numpy as rnm
import json

# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    first_entry = raw_input ("From which entry? (0-220 000) or m as max: ")
    last_entry = 0
    if first_entry != "m":
        last_entry = raw_input ("Until which entry? (0-220 000) or l as last: ")
    
    dataFileName = "~/cernbox/oscilloscope_data/data_1504818689.tree.root"
    pulsePropertiesFileName = "pedestal_noise.json"
    
    data,channels = setUpData(dataFileName,first_entry,last_entry)
    
    pedestal,noise = importNoiseProperties(pulsePropertiesFileName)
    
    amplitudes,risetime = getPulseInfo(data,pedestal,noise)

    print "\n"
    for entry in range(0,len(data)):
        for chan in channels:
            if amplitudes[chan][entry] != 0:
                print "Entry: " + str(int(first_entry)+entry) + " Channel: " + str(chan) +  "\nAmplitude: " +str(amplitudes[chan][entry]) +" mV\nRisetime: "+ str(risetime[chan][entry]) +" ns \n"

# Creates amplitudes and risetime dictionaries and goes through all entries
# and channels. Catches exceptions for KeyErrors
def getPulseInfo(data,pedestal,noise):
    
    amplitudes = dict()
    risetime = dict()
  
    for event in data:
        
        for chan in data.dtype.names:
            
            try:
                amplitudes[chan]
            except Exception, e:
                amplitudes[chan] = np.empty(0)
            
            try:
                risetime[chan]
            except Exception, e:
                risetime[chan] = np.empty(0)
        
            amplitude_entry_channel,risetime_entry_channel = getRisetimeAndAmplitude(event[chan],pedestal[chan])
            
            amplitudes[chan] = np.append(amplitudes[chan],amplitude_entry_channel)
            risetime[chan] = np.append(risetime[chan],risetime_entry_channel)

    return amplitudes, risetime

# Obtains amplitude and risetime values for a entry and channel.
# If no pulse found, the result will be 0 for both amplitude and risetime.
# NB! This code assumes that there is only one pulse per entry.
def getRisetimeAndAmplitude (event, pedestal):
    
    dt = 0.1 # Time scope, in ns
    
    # Set condition on finding the pulse, and select indices where the pulse is.
    points_condition = event<-25*0.001
    pulse_first_index = np.where(points_condition)[0][0] if len( np.where(points_condition)[0] ) else 1002
    pulse_last_index = np.argmin(event)
    
    event = event*1000-pedestal # Convert from V to mV and remove the pedestal
    noise_limit = -25+pedestal # Set 25 mV limit on the noise oscillation curve
    
    pulse_amplitude = np.amin(event)
    pulse_risetime = 0
    
    # How to extract the noise more exactly?
    # The STD for noise is about 2 up to 5 mV,
    # which is not in accordance with data (which is at least 5 mV)
  
  
    if  pulse_amplitude < noise_limit:
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]>0.9*pulse_amplitude) & (event[pulse_first_index:pulse_last_index]<0.1*pulse_amplitude))
        pulse_risetime = (amplitude_indices[-1][0]-amplitude_indices[0][0])*dt
    
    else:
        pulse_amplitude = 0
    
    return pulse_amplitude, pulse_risetime


def setUpData(dataFileName,first,last):
    
    data = ""
    
    if first == "m":
        data = rnm.root2array(dataFileName)
    elif last == "l":
        data = rnm.root2array(dataFileName,start=int(first))
    else:
        data = rnm.root2array(dataFileName,start=int(first),stop=int(last))

    channels = data.dtype.names # gets names for the leafs in TTree file
    return data, channels


def importNoiseProperties(fileName):
    # load from file:
    with open(fileName, 'r') as f:
        try:
            data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            print "The file  " + str(fileName) + " is empty or cannot be read."
            data = {}

    return data["p"], data["n"]

main()
