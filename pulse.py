import ROOT
import numpy as np
import root_numpy as rnm
import json

def pulse():
    end = raw_input ("Until which entry? (0-200 000) or m as max: ")
    dataFileName = "~/cernbox/oscilloscope_data/data_1504818689.tree.root"
    pulsePropertiesFileName = "pedestal_noise2.json"
    data,channels = setUpData(dataFileName,end)
    pedestal,noise = importInfo(pulsePropertiesFileName)


def filterData(data):
    
    for event in data:
        
        for chan in data.dtype.names:
            
            pulse_compatible_samples = event[chan]<-25*0.001
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            

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

pulse()
