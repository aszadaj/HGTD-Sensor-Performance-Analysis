
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import json



##########################################
#                                        #
#                                        #
#             MAIN FUNCTION              #
#                                        #
#                                        #
##########################################


def main():

    data_telescope = importTelescopeData()

    amplitude, risetime, small_amplitude, criticalValues = importPulseProperties()

    #produceTProfileGraphs(amplitude, small_amplitude, data_telescope)

    exit()


##########################################
#                                        #
#                                        #
#              FUNCTIONS                 #
#                                        #
#                                        #
##########################################

#   For future notice, the max and min values for each dimension in the telescope data
#   xMin -5092.44
#   xMax 7053.56
#
#   yMin 6046.8
#   yMax 15174.8

# Define the code to make the analysis
def produceTProfileGraphs(amplitude,small_amplitude, data):

    canvas = ROOT.TCanvas("TProfile2D","TProfile2D")

    histogram2d = ROOT.TProfile2D("test","test",100,-6000,7200,100,6000,15300)
    
    for index in range(0,len(data)):
        # Compare also with small_amplitude, but first the rearrangment must be done
        if data[index]['X'] != -9999 and amplitude["chan0"][index] > 0:
            histogram2d.Fill(data[index]['X'], data[index]['Y'], amplitude['chan0'][index])

    canvas.cd()
    histogram2d.Draw("COLZ")
    canvas.Update()
    filename = "plot_telescope/testplot.pdf"
    canvas.Print(filename)



# Note, the file have only 200K entries
def importTelescopeData():
  
    dataFileName = "~/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/tracking1504818689.root"
    data = rnm.root2array(dataFileName) # numpy array, 200K elements (equivalent to no of entries), each element x and y values in micrometers
  
    return data


# The file have 200 263 entries, reduced to 200K to adapt to telescope data
def importOscilloscopeData():
    
    # Prompt for reading in how many values should be considered
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
    
    fileName = "resources/pedestal.json"
    
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
    
    amplitude = "" # Max amplitude value for each entry and channel
    risetime = "" # Rise time for the same amplitude, entry and channel correspondingly
    small_amplitude = "" # Max amplitude values for which rise time could not be calculated, due to insufficient points
    criticalValues = "" # Maximal value for writing out data from the physical oscilloscope to data
    
    # Note: amplitude values are corrected with a pedestal (from the noise analysis) and the critical values are not
    with open("resources/pulse_info.pkl","rb") as input:
        
        amplitude = pickle.load(input)          # dictionary, keys: channels, for each key list of amplitude values (200K)
        risetime = pickle.load(input)           # dictionary, keys: channels, for each key list of rise time values (200K)
        small_amplitude = pickle.load(input)    # dictionary, keys: channels, for each key list of small amplitude values (<< 200K)
        criticalValues = pickle.load(input)     # dictionary, keys: channels, for each key value for maximal value of reading in from the oscilloscope (1 value per channel)
    
    # Convert all values to positive
    amplitude.update((x, y*-1) for x, y in amplitude.items())
    small_amplitude.update((x, y*-1) for x, y in small_amplitude.items())
    criticalValues.update((x, y*-1) for x, y in criticalValues.items())
    
    # Constrain to 200K values
    for chan in amplitude.keys():
        amplitude[chan] = amplitude[chan][0:-263]
        risetime[chan] = risetime[chan][0:-263]


    return amplitude, risetime, small_amplitude, criticalValues
    

# Gets sensor names specifically for run 3656 for Sep 2017
def getSensorsNames():
    sensors = {'chan5': 'W4-S215', 'chan4': 'W4-S215', 'chan7': 'W4-S215', 'chan6': 'W4-S215', 'chan1': '50D-GBGR2', 'chan0': 'W9-LGA35', 'chan3': 'SiPM-AFP', 'chan2': 'W4-LG12'}
    return sensors


##########################################
#                                        #
#                                        #
#               MAIN()                   #
#                                        #
#                                        #
##########################################

main()

