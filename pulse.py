
import ROOT
import numpy as np
import root_numpy as rnm
import json
import pickle


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
  
    data, sensors, first_entry, last_entry = importFileData()
    
    setGlobalVariables(data.dtype.names)
    
    findCriticalValues(data,criticalValues)
    
    amplitudes, risetimes = getPulseInfo(data)
 
    #produceDistributionPlots(amplitudes, risetimes, sensors)
    
    exportResults(amplitudes, risetimes, small_amplitudes, criticalValues)
  
    exit()

# Creates dictionaries for amplitudes and rise time where each key defines the channel and for each key
# there is a list of obtained amplitudes, where each index corresponds to an entry.
# E.g amplitudes["chan1"][233]: amplitude value for channel chan0 and entry 233
def getPulseInfo(data):
    
    channels = data.dtype.names
    pedestal = importNoiseProperties()
    
    amplitudes = dict()
    risetimes = dict()
    
    for chan in channels:
        
        amplitudes[chan] = np.empty(0)
        risetimes[chan] = np.empty(0)
       
    for entry in range(0,len(data)):
        
        for chan in channels:
            
            convert_mV = 1000 # V to mV
            
            amplitude_entry_channel, risetime_entry_channel = getAmplitudeRisetime(data[entry][chan]*convert_mV, pedestal[chan], chan, entry)
            
            amplitudes[chan] = np.append(amplitudes[chan], amplitude_entry_channel)
            risetimes[chan] = np.append(risetimes[chan], risetime_entry_channel)

    return amplitudes, risetimes


# Calculates amplitude and rise time for selected entry and channel. It returns a zero value if:
# 1. It is not sufficiently high (for now, set as -35 mV)
# 2. Cannot be calculated, due to insufficient points
def getAmplitudeRisetime (event, pedestal, chan, entry):
    
    dt = 0.1 # Time scope, in ns
    noise_limit = -25 # Limit to select amplitudes above the noise level
    
    # Set condition on finding the pulse, and select indices where the pulse is.
    indices_condition = event < noise_limit
    
    pulse_amplitude = 0
    pulse_risetime = 0
    
    if any(indices_condition):
        
        pulse_first_index = np.where(indices_condition)[0][0] - 3
        pulse_last_index = np.argmin(event)
       
        pulse_amplitude = np.amin(event)-pedestal
        
        # Select indices which are between 10% and 90% of the pulse.
        amplitude_indices = np.argwhere((event[pulse_first_index:pulse_last_index]>0.9*np.amin(event)) & (event[pulse_first_index:pulse_last_index]<0.1*np.amin(event)))
        
        try:
            pulse_risetime = (amplitude_indices[-1][0] - amplitude_indices[0][0])*dt
        
        except Exception, e:
            small_amplitudes[chan][entry] = pulse_amplitude
            pulse_amplitude = 0
            pulse_risetime = 0

    return pulse_amplitude, pulse_risetime

# Searches for minimal values for all data points, per channel.
# The oscilloscope is designed in such way, that it cannot write down data
# below a critical value
def findCriticalValues(data,criticalValues):
    
    for chan in data.dtype.names:
        
        for entry in data[chan]:
       
            if criticalValues[chan] > np.amin(entry):
                criticalValues[chan] = np.amin(entry)

    criticalValues.update((x, y*1000) for x, y in criticalValues.items())

# Create 8 plots, for each channel across all entries, for amplitudes and rise times
def produceDistributionPlots(amplitudes,risetimes,sensors):
    
    canvas_amplitude = ROOT.TCanvas("amplitude", "Amplitude Distribution")
    canvas_risetime = ROOT.TCanvas("risetime", "Risetime Distribution")

    amplitude_graph = dict()
    risetime_graph = dict()
    
    for chan in amplitudes.keys():
        
        amplitude_graph[chan] = ROOT.TH1D("amplitude_"+chan,"Amplitude "+chan,800,-400,0)
        risetime_graph[chan] = ROOT.TH1D("risetime_"+chan,"Risetime "+chan,50,0,1)
        
        index = int(chan[-1:])
        
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0 and risetimes[chan][entry] != 0 and amplitudes[chan][entry] > criticalValues[chan]+2:
                amplitude_graph[chan].Fill(amplitudes[chan][entry])
                risetime_graph[chan].Fill(risetimes[chan][entry])

        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitude_graph[chan],canvas_amplitude,typeOfGraph,sensors[index],chan)

        typeOfGraph = "risetime"
        defineAndProduceHistogram(risetime_graph[chan],canvas_risetime,typeOfGraph,sensors[index],chan)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,sensor,chan):
    
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "pulse_distributions/rise_time_distribution_"+chan+".pdf"
    titleAbove = "Distribution of rise times, oscilloscope for Sep 2017 Run 3656, for channel " + chan + ", sensor: " + str(sensor)
    
    if typeOfGraph == "amplitude":
    
        xAxisTitle = "Amplitude (mV)"
        fileName = "pulse_distributions/amplitude_distribution_"+chan+".pdf"
        titleAbove = "Distribution of amplitudes, oscilloscope for Sep 2017 Run 3656, for channel " + chan + ", sensor: " + str(sensor)

    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)


# Prompt for choosing entry 
def importFileData():
    
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
    
    # Note, these names are specific for the file specified above
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



# Export dictionaries amplitude and risetime and list of channels in a .pkl file
def exportResults(amplitude,risetime,small_amplitudes,criticalValues):
    
    with open("pulse_info.pkl","wb") as output:
        
        pickle.dump(amplitude,output,pickle.HIGHEST_PROTOCOL)
        
        pickle.dump(risetime,output,pickle.HIGHEST_PROTOCOL)

        pickle.dump(small_amplitudes,output,pickle.HIGHEST_PROTOCOL)

        pickle.dump(criticalValues,output,pickle.HIGHEST_PROTOCOL)


# Define global variables small_amplitudes and criticalValue to be used in
# findCriticalValues(data,criticalValues) and getAmplitudeRisetime(event, pedestal, chan, entry)
def setGlobalVariables(channels):

    global small_amplitudes
    global criticalValues
    small_amplitudes = dict()
    criticalValues = dict()

    for chan in channels:
        small_amplitudes[chan] = np.zeros(200263)
        criticalValues[chan] = 0



############# MAIN #############

main()

################################

