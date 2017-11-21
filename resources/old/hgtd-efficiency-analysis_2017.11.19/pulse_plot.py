
import ROOT
import numpy as np


# Create 8 plots, for each channel across all entries, for amplitudes and rise times
def producePulseDistributionPlots(amplitudes,risetimes,sensors,pedestals,runNumber,timeStamp,small_amplitudes):
    
    canvas_amplitude = ROOT.TCanvas("Amplitude Distribution", "amplitude")
    canvas_risetime = ROOT.TCanvas("Risetime Distribution", "risetime")

    amplitude_graph = dict()
    risetime_graph = dict()
    
    for chan in amplitudes.dtype.names:
        
        amplitude_graph[chan] = ROOT.TH1D("Amplitude channel "+str(int(chan[-1:])+1),"amplitude"+chan,900,0,400)
        risetime_graph[chan] = ROOT.TH1D("Rise time channel "+str(int(chan[-1:])+1),"risetime"+chan,50,0,1)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0 and risetimes[chan][entry] != 0:
                amplitude_graph[chan].Fill(amplitudes[chan][entry])
                risetime_graph[chan].Fill(risetimes[chan][entry])

        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitude_graph[chan],canvas_amplitude,typeOfGraph,sensors,chan,runNumber,timeStamp)

        typeOfGraph = "risetime"
        defineAndProduceHistogram(risetime_graph[chan],canvas_risetime,typeOfGraph,sensors,chan,runNumber,timeStamp)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,sensors,chan,runNumber,timeStamp):
    
    chan_index = int(chan[-1:])
   
    titleAbove = "Distribution of pulse rise times, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "plots/pulse_distributions/rise_time_distribution_"+str(runNumber)+"_"+chan+".pdf"
    
    
    if typeOfGraph == "amplitude":
    
        titleAbove = "Distribution of pulse amplitudes, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Amplitude (mV)"
        fileName = "plots/pulse_distributions/amplitude_distribution_"+str(runNumber)+"_"+chan+".pdf"
    

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


