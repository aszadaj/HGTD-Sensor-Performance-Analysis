
import ROOT
#import langaus # a C-file which determines landau(*)gauss fit, future project
import numpy as np
import root_numpy as rnm
import json


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    
    errors = 0 # Pulses which cannot be calculated
    
    data, sensors, first_entry, last_entry = importFileData()
   
    pedestal = importNoiseProperties()
    
    amplitudes, risetimes, errors = getPulseInfoForAllEntriesAndChannels(data, pedestal, errors)
    
    produceDistributionPlots(amplitudes, risetimes, data.dtype.names, sensors)
    
    #printAllValues(data.dtype.names, sensors, amplitudes, risetimes, first_entry, last_entry)
    
#    # about 3% of all pulses cannot be calculated.
#    print "Errors: " + str(errors)
#    print "Percentage: " + str(float(errors)/float(len(data))*8)

    exit()

# Creates amplitudes and risetime dictionaries and goes through all entries
# and channels. Catches exceptions for KeyErrors
def getPulseInfoForAllEntriesAndChannels(data, pedestal, errors):
    
    amplitudes = dict()
    risetime = dict()
    entry = 0
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
          
            amplitude_entry_channel, risetime_entry_channel, errors = getRisetimeAndAmplitude(event[chan], pedestal[chan], chan, entry, errors)
            
            amplitudes[chan] = np.append(amplitudes[chan], amplitude_entry_channel)
            risetime[chan] = np.append(risetime[chan], risetime_entry_channel)
            
        entry += 1

    return amplitudes, risetime, errors


# Obtains amplitude and risetime values for a entry and channel. Also obtains how many pulses cannot be calculated
# If no pulse found, the result will be 0 for both amplitude and risetime.
# NB1! This code assumes that there is only one pulse per entry.
# NB2! Fitting minimal value by evaluating points is usally not the best way, it
# decreases in realiablity, one could use instead a Landau(*)Gauss distribution fit
def getRisetimeAndAmplitude (event, pedestal, chan, entry, errors):
    
    dt = 0.1 # Time scope, in ns
    
    # Set condition on finding the pulse, and select indices where the pulse is.
    points_condition = event<-20*0.001
    pulse_first_index = np.where(points_condition)[0][0] if len(np.where(points_condition)[0]) else 1002
    pulse_last_index = np.argmin(event)
    
    # check pedestal sign
    event = event*1000 # Convert from V to mV
    pulse_limit = -30-pedestal # Set 30 mV limit on the noise oscillation curve
    
    pulse_amplitude = np.amin(event)-pedestal
    pulse_risetime = 0
    
    if  pulse_amplitude < pulse_limit: # clear problem here, in entry 52 chan4 there is a small pulse
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]>0.9*pulse_amplitude) & (event[pulse_first_index:pulse_last_index]<0.1*pulse_amplitude))
        
        try:
            pulse_risetime = (amplitude_indices[-1][0] - amplitude_indices[0][0])*dt
        except Exception, e:
            #print "\nProblem with computing pulse risetime for channel " + str(chan) +" entry " + str(entry) +"\n"
            #pulse_amplitude = 0 # If the rise time cannot be calculated, set the amplitude to zero, since it is small
            errors += 1

    else:
        pulse_amplitude = 0
    
    return pulse_amplitude, pulse_risetime, errors


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


# Print non-zero amplitude and risetime values and show for which channel and entry they represent
def printAllValues(channels, sensors, amplitudes, risetime, first_entry, last_entry):
        
    print "\n"
    for entry in range(0,len(amplitudes[channels[0]])):
        for chan in channels:
            index = 0
            if amplitudes[chan][entry] != 0:
                print "Entry: " + str(int(first_entry)+entry+1) + " Sensor: " + str(sensors[index]) +", Channel: " + str(chan) +  "\nAmplitude: " +str("%.2f" % amplitudes[chan][entry]) +" mV\nRisetime: "+ str(risetime[chan][entry]) +" ns \n"
            index += 1               

        
# Create 8 plots, for each channel across all entries, for amplitudes and risetime
def produceDistributionPlots(amplitudes,risetimes,channels,sensors):
    
    canvas_amplitude = ROOT.TCanvas("amplitude", "Amplitude Distribution")
    canvas_risetime = ROOT.TCanvas("risetime", "Risetime Distribution")
    
    index = 0
    
    yAxisLimits_amplitude = [220,250,300,1500,200,200,200,200]
    
    for chan in channels:

        amplitude_graph = ROOT.TH1D("amplitude_"+chan,"Amplitude "+chan,1000,-450,0)
        risetime_graph = ROOT.TH1D("risetime_"+chan,"Risetime "+chan,100,0,1)
        
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0:
                amplitude_graph.Fill(amplitudes[chan][entry])
                risetime_graph.Fill(risetimes[chan][entry])
        
        titleAbove = "Distribution of amplitudes, oscilloscope for Sep 17 Run 3656, for channel " + chan + ", sensor: " + str(sensors[index])
        xAxisTitle = "Amplitude (mV)"
        yAxisTitle = "Number (N)"
        
        setGraphAttributes(amplitude_graph,titleAbove,xAxisTitle,yAxisTitle)
        
        amplitude_graph.SetMaximum(yAxisLimits_amplitude[index])
        
        titleAbove = "Distribution of rise times, oscilloscope for Sep 17 Run 3656, for channel " + chan + ", sensor: " + str(sensors[index])
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        setGraphAttributes(risetime_graph,titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "pulse_distributions/amplitude_distribution_"+chan+".pdf"
        exportGraph(amplitude_graph,canvas_amplitude,fileName)
        
        fileName = "pulse_distributions/risetime_distribution_"+chan+".pdf"
        exportGraph(risetime_graph,canvas_risetime,fileName)

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



############# MAIN #############

main()

################################

