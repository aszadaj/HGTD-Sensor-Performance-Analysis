
import ROOT
import numpy as np

import metadata as md


# Create 8 plots, for each channel across all entries, for amplitudes and rise times
def producePulseDistributionPlots(amplitudes, rise_times, pedestals):
    
    canvas_amplitude = ROOT.TCanvas("Amplitude Distribution", "amplitude")
    canvas_rise_time = ROOT.TCanvas("Risetime Distribution", "risetime")

    amplitudes_graph = dict()
    rise_times_graph = dict()
    
    for chan in amplitudes.dtype.names:
        
        amplitudes_graph[chan] = ROOT.TH1D("Amplitude channel "+ str(int(chan[-1:])+1), "amplitude" + chan,900, 0, 400)
        rise_times_graph[chan] = ROOT.TH1D("Rise time channel " + str(int(chan[-1:])+1), "rise_time" + chan, 50 ,0 ,1)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0 and rise_times[chan][entry] != 0:
                amplitudes_graph[chan].Fill(amplitudes[chan][entry])
                rise_times_graph[chan].Fill(rise_times[chan][entry])

        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitudes_graph[chan],canvas_amplitude,typeOfGraph,chan)
        typeOfGraph = "rise_time"
        defineAndProduceHistogram(rise_times_graph[chan],canvas_rise_time,typeOfGraph,chan)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,chan):
    sensors = md.getSensorNames()
    chan_index = int(chan[-1:])
    
    titleAbove = "Distribution of pulse rise times, Sep 2017 run "+str(md.getRunNumber())+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "plots/pulse_distributions/rise_time_plots/rise_time_distribution_"+str(md.getRunNumber())+"_"+chan+".pdf"
    
    
    if typeOfGraph == "amplitude":
    
        titleAbove = "Distribution of pulse amplitudes, Sep 2017 run "+str(md.getRunNumber())+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Amplitude (mV)"
        fileName = "plots/pulse_distributions/amplitude_plots/amplitude_distribution_"+str(md.getRunNumber())+"_"+chan+".pdf"
    

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


