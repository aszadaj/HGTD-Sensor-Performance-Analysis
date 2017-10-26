
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import json


##########################################
#
#
#               MAIN FUNCTION
#
#
##########################################

# Note: amplitude is pedestal corrected, whereas criticalValues are not
def main():

    # data here is an array, each index (x,y)
    data_telescope = importTelescopeData()
    
    amplitude, risetime, small_amplitude, criticalValues = importPulseProperties()

    exit()



##########################################
#
#
#               FUNCTIONS
#
#
##########################################


# Note, the file have only 200K entries
def importTelescopeData():
  
    dataFileName = "~/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/tracking1504818689.root"
    data = rnm.root2array(dataFileName)
    
    return data

# The file have 200 263 entries, reduced to 200K to adapt to telescope data
def importRunData():
    
    first_entry = raw_input ("From which entry? (0-200 000) or 'm' as max: ")
    last_entry = 0
    
    if first_entry != "m":
        
        last_entry = raw_input ("Until which entry? ("+str(first_entry)+"-200 000) or 'l' as last: ")
        
        if last_entry == "l":
            
            last_entry = 200000
    else:
        
        first_entry = 0
        last_entry = 200000
    
    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_1504818689.tree.root"

    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))
    
    # Invert minus sign and change from V to mV
    for chan in data.dtype.names:
        data[chan] = np.multiply(data[chan],-1000)
    
    return data, int(first_entry), int(last_entry)


# Import JSON file for pedestal and noise information from noise analysis
def importNoiseProperties():
    
    fileName = "pedestal.json"
    
    # load from file:
    with open(fileName, 'r') as f:
        
        try:
            data = json.load(f)
        
        # if the file is empty the ValueError will be thrown
        except ValueError:
            
            print "The file  " + str(fileName) + " is empty or cannot be read."
            data = {}

    return data["p"]


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importPulseProperties():
    
    amplitude = ""
    risetime = ""
    small_amplitude = ""
    criticalValues = ""
    
    with open("pulse_info_backup.pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
        small_amplitude = pickle.load(input)
        criticalValues = pickle.load(input)
    
    # Convert all values to positive
    amplitude.update((x, y*-1) for x, y in amplitude.items())
    small_amplitude.update((x, y*-1) for x, y in small_amplitude.items())
    criticalValues.update((x, y*-1) for x, y in criticalValues.items())
    
    # Constrain to 200K values
    for chan in amplitude.keys():
        amplitude[chan] = amplitude[chan][0:-263]
        risetime[chan] = risetime[chan][0:-263]


    return amplitude, risetime, small_amplitude, criticalValues
    

def getSensorsNames():
    sensors = {'chan5': 'W4-S215', 'chan4': 'W4-S215', 'chan7': 'W4-S215', 'chan6': 'W4-S215', 'chan1': '50D-GBGR2', 'chan0': 'W9-LGA35', 'chan3': 'SiPM-AFP', 'chan2': 'W4-LG12'}
    return sensors


##########################################
#
#
#               MAIN()
#
#
##########################################

main()

