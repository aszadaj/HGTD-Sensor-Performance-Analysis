
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import pandas as pd


def produceNoiseDistributionPlots(noise_average, noise_std, runNumber, sensors):

    channels = noise_average.dtype.names
    pedestal = dict()
    noise = dict()

    for chan in channels:
        
        pedestal[chan] = ROOT.TH1D("Pedestal channel "+str(int(chan[-1:])+1),"pedestal"+chan,300,-5,5)
        noise[chan] = ROOT.TH1D("Noise channel "+str(int(chan[-1:])+1),"noise"+chan,300,0,7)
    
        for entry in range(0,len(noise_average)):
            pedestal[chan].Fill(noise_average[entry][chan])
            noise[chan].Fill(noise_std[entry][chan])
    
    canvas_pedestal = ROOT.TCanvas("Pedestal per channel", "Pedestal per channel")
    canvas_noise = ROOT.TCanvas("Noise per channel", "Noise per channel")
   
    for chan in channels:
    
        chan_index = int(chan[-1:])
        
        titleAbove = "Distribution of noise mean values from each entry, run "+str(runNumber)+", channel " + str(chan_index+1) +", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Noise mean value (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(pedestal[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        titleAbove = "Distribution of standard deviation values (noise) from each entry, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(noise[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "plots/pedestal_distributions/pedestal_"+str(runNumber)+"_"+chan+".pdf"
        exportGraph(pedestal[chan],canvas_pedestal,fileName)
        
        fileName = "plots/pedestal_distributions/noise_"+str(runNumber)+"_"+chan+".pdf"
        exportGraph(noise[chan],canvas_noise,fileName)


# Define the setup for graphs
# Input: dictionary with TH1 objects, and title information for the graph
def setGraphAttributes(graphList,titleAbove,xAxisTitle,yAxisTitle):
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)

# Produce PDF file for selected chan
# Input: dictionary with TH1 objects, TCanvas object and filename for the produced file
# Output: mean value for selected dictionary and chan
def exportGraph(graphList,canvas,fileName):
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)



