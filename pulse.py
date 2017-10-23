
import ROOT
import numpy as np
import root_numpy as rnm
import json
import pickle


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
  
    data, sensors, first_entry, last_entry = importFileData()
    
    amplitudes, risetimes = getPulseInfoForAllEntriesAndChannels(data)
    
    produceDistributionPlots(amplitudes, risetimes, data.dtype.names, sensors)
    
    exportInfo(amplitudes, risetimes,data.dtype.names)
   
    exit()

# Creates amplitudes and risetime dictionaries and goes through all entries and channels.
def getPulseInfoForAllEntriesAndChannels(data):
    
    channels = data.dtype.names
    pedestal = importNoiseProperties()
    
    amplitudes = dict()
    risetimes = dict()
    
    for chan in channels:
        
        amplitudes[chan] = np.empty(0)
        risetimes[chan] = np.empty(0)
   
   
    for entry in range(0,len(data)):
        
        for chan in channels:
            
            amplitude_entry_channel, risetime_entry_channel = getRisetimeAndAmplitude(data[entry][chan], pedestal[chan], chan, entry)
            
            amplitudes[chan] = np.append(amplitudes[chan], amplitude_entry_channel)
            risetimes[chan] = np.append(risetimes[chan], risetime_entry_channel)


    return amplitudes, risetimes


# Obtains amplitude and risetime values for a entry and channel. Also obtains how many pulses cannot be calculated
# If no pulse found, the result will be 0 for both amplitude and risetime.
# NB1! This code assumes that there is only one pulse per entry.
# NB2! Fitting minimal value by evaluating points is usally not the best way, it
# decreases in realiablity, one could use instead a distribution fit
def getRisetimeAndAmplitude (event, pedestal, chan, entry):
    
    dt = 0.1 # Time scope, in ns
    
    # Set condition on finding the pulse, and select indices where the pulse is.
    indices_condition = event<-20*0.001
    
    pulse_amplitude = 0
    pulse_risetime = 0
    
    if any(indices_condition):
        
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmin(event)
        
        event = event*1000 # Convert from V to mV
        pulse_limit = -40-pedestal # Set 40 mV to consider it as a pulse
        
        pulse_amplitude = np.amin(event)-pedestal
        
        criticalValue = -354.7959327-pedestal
        criticalValue_chan3 = -383.29595327-pedestal
        
        if  pulse_amplitude < pulse_limit and pulse_amplitude > criticalValue_chan3:
            
            if chan != "chan3" and pulse_amplitude < criticalValue:
                pulse_amplitude = 0
            
            else:
                
                # Select indices which are between 10% and 90% of the pulse.
                amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]>0.9*pulse_amplitude) & (event[pulse_first_index:pulse_last_index]<0.1*pulse_amplitude))
                
                try:
                    pulse_risetime = (amplitude_indices[-1][0] - amplitude_indices[0][0])*dt
                except Exception, e:
                    pulse_amplitude = 0

        else:
            pulse_amplitude = 0
    
    return pulse_amplitude, pulse_risetime


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


# Create 8 plots, for each channel across all entries, for amplitudes and risetime
def produceDistributionPlots(amplitudes,risetimes,channels,sensors):
    
    canvas_amplitude = ROOT.TCanvas("amplitude", "Amplitude Distribution")
    canvas_risetime = ROOT.TCanvas("risetime", "Risetime Distribution")
    
    index = 0
    
    yAxisLimits_amplitude = [250,250,350,1200,200,200,200,200]
    
    amplitude_graph = dict()
    risetime_graph = dict()
    
    for chan in channels:
        amplitude_graph[chan] = ROOT.TH1D("amplitude_"+chan,"Amplitude "+chan,1000,-400,0)
        risetime_graph[chan] = ROOT.TH1D("risetime_"+chan,"Risetime "+chan,100,0,1)
    
    
    for chan in channels:
        
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0:
                amplitude_graph[chan].Fill(amplitudes[chan][entry])
                risetime_graph[chan].Fill(risetimes[chan][entry])
        
        titleAbove = "Distribution of amplitudes, oscilloscope for Sep 17 Run 3656, for channel " + chan + ", sensor: " + str(sensors[index])
        xAxisTitle = "Amplitude (mV)"
        yAxisTitle = "Number (N)"
        
        setGraphAttributes(amplitude_graph[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        amplitude_graph[chan].SetMaximum(yAxisLimits_amplitude[index])
        
        titleAbove = "Distribution of rise times, oscilloscope for Sep 17 Run 3656, for channel " + chan + ", sensor: " + str(sensors[index])
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        setGraphAttributes(risetime_graph[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "pulse_distributions/amplitude_distribution_"+chan+".pdf"
        exportGraph(amplitude_graph[chan],canvas_amplitude,fileName)
        
        fileName = "pulse_distributions/risetime_distribution_"+chan+".pdf"
        exportGraph(risetime_graph[chan],canvas_risetime,fileName)

        index += 1


# Define TH1 properties
def setGraphAttributes(graphList,titleAbove,xAxisTitle,yAxisTitle):
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)


# Draw the graph and export it as PDF
def exportGraph(graphList,canvas,fileName):
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)


def exportInfo(amplitude,risetime,channels):
    
    with open("amplitude_risetime.pkl","wb") as output:
        
        pickle.dump(amplitude,output,pickle.HIGHEST_PROTOCOL)
        
        pickle.dump(risetime,output,pickle.HIGHEST_PROTOCOL)

        pickle.dump(channels,output,pickle.HIGHEST_PROTOCOL)


def printGraph(data_points,entry,channel):

    canvas = ROOT.TCanvas("Waveforms", "Waveforms")
    
    dt = 0.1

    graph = ROOT.TGraph(len(data_points))
    graph.SetLineColor(1)
    graph.SetMarkerColor(1)
    
    for i in range(0,len(data_points)):
        graph.SetPoint(i, i*dt, data_points[i])

    drawOpt = "LPA"
    graph.Draw(drawOpt)
    graph.GetYaxis().SetRangeUser(min(data_points)*1.2, max(data_points)*2)
    graph.Draw(drawOpt)

    canvas.cd()
    canvas.Update()
    plotName ="graphs/plot_entry" + str(entry) +"_"+str(channel) +".pdf"
    canvas.Print(plotName)





############# MAIN #############

main()

################################

