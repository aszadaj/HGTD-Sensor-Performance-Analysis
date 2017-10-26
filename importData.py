
import ROOT
import numpy as np
import pickle
import root_numpy as rnm
import json
#from pulse import importNoiseProperties


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    
    data, sensors, first_entry, last_entry = importRunData()
    
    amplitude, risetime, small_amplitude, criticalValues = importPulseProperties()
    
    pedestal = importNoiseProperties()
    
    exit()


# Produce a TGraph for selected waveform
def printGraph(data_points,entry,channel,sensor,amplitude):
    
    canvas = ROOT.TCanvas("Waveforms", "Waveforms")
    
    dt = 0.1
    
    graph = ROOT.TGraph(len(data_points))
   
    for i in range(0,len(data_points)):
        graph.SetPoint(i, i*dt, data_points[i])
    
    yAxisTitle = "Voltage (mV)"
    xAxisTitle = "Time in entry "+str(entry)+" (ns)"
    setTitleAboveGraph = "Plots with critical amplitude value for entry " + str(entry) + ", " +str(channel)+ ", sensor: " + str(sensor)
    drawOpt = "LPA"
    graph.SetLineColor(1)
    graph.SetMarkerColor(1)
    graph.GetYaxis().SetTitle(yAxisTitle)
    graph.GetXaxis().SetTitle(xAxisTitle)
    graph.SetTitle(setTitleAboveGraph)
    graph.GetYaxis().SetRangeUser(min(data_points)*1.2, max(data_points)*1.2)
    graph.Draw(drawOpt)

    canvas.cd()
    canvas.Update()
    plotName ="plots/plot_" + str(channel) +"_entry_"+str(entry) +".pdf"
    canvas.Print(plotName)



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
    
    return amplitude, risetime, small_amplitude, criticalValues


# Prompt for choosing entry
def importRunData():
    
    first_entry = raw_input ("From which entry? (0-200 263) or 'm' as max: ")
    last_entry = 0
    
    if first_entry != "m":
        
        last_entry = raw_input ("Until which entry? ("+str(first_entry)+"-200 263) or 'l' as last: ")
        
        if last_entry == "l":
            
            last_entry = 200263
    else:
        
        first_entry = 0
        last_entry = 200263
    
    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_1504818689.tree.root"

    sensor = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]
    sensors = dict()
    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))
    #data = rnm.root2array(dataFileName)
    
    for chan in data.dtype.names:
        sensors[chan] = sensor[int(chan[-1:])]
        data[chan] = np.multiply(data[chan],-1000)
    
    return data, sensors, int(first_entry), int(last_entry)


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


def printGraphsCriticalAmplitude():

    for chan in amplitude.keys():
        positions = np.argwhere(amplitude[chan]-pedestal[chan] == criticalValues[chan])
        index1 = 4
        index2 = 0
        printGraph(data[chan][positions[index1][index2]],positions[index1][index2],chan,sensors[chan],amplitude[chan][positions[index1][index2]])


############# MAIN #############

main()

################################

