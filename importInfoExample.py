
import ROOT
import numpy as np
import pickle
import root_numpy as rnm
import json
#from pulse import importNoiseProperties


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    
    data, sensors, first_entry, last_entry = importFileData()
    
    amplitude, risetime = importInfo()
    
    pedestal = importNoiseProperties()
    
    printValues(amplitude)
   
    exit()



# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importInfo():
    
    amplitude = ""
    risetime = ""
    
    with open("pulse_all_entries_distributions/amplitude_rise_time_all_entries.pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)

    return amplitude, risetime


# Print out all non-zero values
def printValues(infoDictionary):
    
    channels = infoDictionary.keys()
    
    print channels
    
    for chan in channels:
        print chan
        for index in range(0,len(infoDictionary[chan])):
            if infoDictionary[chan][index] != 0:
                print str(index) + ": " + str(infoDictionary[chan][index])
        print "\n"


# Prompt for choosing entry
def importFileData():
    
    first_entry = raw_input ("From which entry? (0-220 000) or 'm' as max: ")
    last_entry = 0
    
    if first_entry != "m":
        
        last_entry = raw_input ("Until which entry? ("+str(first_entry)+"-220 000) or 'l' as last: ")
        
        if last_entry == "l":
            
            last_entry = 200263
    else:
        
        first_entry = 0
        last_entry = 200263
    
    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_1504818689.tree.root"

    sensors = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]

    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))
    
    return data, sensors, first_entry, last_entry


# Produce a TGraph for selected waveform
def printGraph(data_points,entry,channel,sensor,pedestal,amplitude):
    
    canvas = ROOT.TCanvas("Waveforms", "Waveforms")
    
    dt = 0.1
    
    graph = ROOT.TGraph(len(data_points))
   
    for i in range(0,len(data_points)):
        graph.SetPoint(i, i*dt, data_points[i]-pedestal)
    
    yAxisTitle = "Voltage (mV)"
    xAxisTitle = "Time in entry "+str(entry)+" (ns)"
    setTitleAboveGraph = "Waveform for entry " + str(entry) + ", " +str(channel)+ ", sensor: " + str(sensor) + ", amplitude: " + str("%.2f" % amplitude) +" mV"
    drawOpt = "LPA"
    graph.SetLineColor(1)
    graph.SetMarkerColor(1)
    graph.GetYaxis().SetTitle(yAxisTitle)
    graph.GetXaxis().SetTitle(xAxisTitle)
    graph.SetTitle(setTitleAboveGraph)
    graph.GetYaxis().SetRangeUser(min(data_points)*1.2, max(data_points)*2)
    graph.Draw(drawOpt)

    canvas.cd()
    canvas.Update()
    plotName ="plot_" + str(channel) +"_entry_"+str(entry) +".pdf"
    canvas.Print(plotName)

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




############# MAIN #############

main()

################################

