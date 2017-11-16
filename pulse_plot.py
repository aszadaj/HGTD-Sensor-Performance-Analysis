
import ROOT
import numpy as np


# Create 8 plots, for each channel across all entries, for amplitudes and rise times
def producePulseDistributionPlots(amplitudes,risetimes,sensors,pedestals,runNumber,timeStamp,small_amplitudes):
    
    canvas_amplitude = ROOT.TCanvas("amplitude", "Amplitude Distribution")
    canvas_risetime = ROOT.TCanvas("risetime", "Risetime Distribution")

    amplitude_graph = dict()
    risetime_graph = dict()
    
    for chan in amplitudes.dtype.names:
        
        amplitude_graph[chan] = ROOT.TH1D("amplitude_"+chan,"Amplitude "+chan,800,0,400)
        risetime_graph[chan] = ROOT.TH1D("risetime_"+chan,"Risetime "+chan,50,0,1)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0 and risetimes[chan][entry] != 0:
                amplitude_graph[chan].Fill(amplitudes[chan][entry])
                risetime_graph[chan].Fill(risetimes[chan][entry])

        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitude_graph[chan],canvas_amplitude,typeOfGraph,sensors[index],chan,runNumber,timeStamp)

        typeOfGraph = "risetime"
        defineAndProduceHistogram(risetime_graph[chan],canvas_risetime,typeOfGraph,sensors[index],chan,runNumber,timeStamp)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,sensor,chan,runNumber,timeStamp):
    
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "pulse_distributions/rise_time_distribution_"+str(runNumber)+"_"+chan+".pdf"
    titleAbove = "Distribution of rise times, oscilloscope for Sep 2017 Run "+str(runNumber)+", for channel " + chan + ", sensor: " + str(sensor)
    
    if typeOfGraph == "amplitude":
    
        xAxisTitle = "Amplitude (mV)"
        fileName = "pulse_distributions/amplitude_distribution_"+str(runNumber)+"_"+chan+".pdf"
        titleAbove = "Distribution of amplitudes, oscilloscope for Sep 2017 Run "+str(runNumber)+", for channel " + chan + ", sensor: " + str(sensor)

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


