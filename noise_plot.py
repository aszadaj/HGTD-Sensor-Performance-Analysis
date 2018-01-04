import ROOT
import metadata as md
import numpy as np


def produceNoiseDistributionPlots(noise_average, noise_std):
    
    channels = noise_average.dtype.names
    pedestal_graph = dict()
    noise_graph = dict()
    
    for chan in channels:
    
        pedestal_low   = np.amin(np.take(noise_average[chan], np.nonzero(noise_average[chan]))[0])*0.9
        pedestal_max   = np.amax(np.take(noise_average[chan], np.nonzero(noise_average[chan]))[0])*1.1
        noise_low      = np.amin(np.take(noise_std[chan], np.nonzero(noise_std[chan]))[0])*0.9
        noise_max      = np.amax(np.take(noise_std[chan], np.nonzero(noise_std[chan]))[0])*1.1
        
        pedestal_graph[chan] = ROOT.TH1D("Pedestal, channel "+str(int(chan[-1:])+1), "pedestal"+chan, 1000, pedestal_low, pedestal_max)
        noise_graph[chan]    = ROOT.TH1D("Noise, channel "+str(int(chan[-1:])+1), "noise"+chan, 1000, noise_low, noise_max)


        for entry in range(0,len(noise_average)):
        
            if noise_average[entry][chan] != 0:
                pedestal_graph[chan].Fill(noise_average[entry][chan])
                noise_graph[chan].Fill(noise_std[entry][chan])
    
    canvas_pedestal = ROOT.TCanvas("Pedestal per channel", "Pedestal per channel")
    canvas_noise = ROOT.TCanvas("Noise per channel", "Noise per channel")
   
    for chan in channels:
    
        titleAbove = "Distribution of standard deviation values (noise) from each entry, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(noise_graph[chan], titleAbove, xAxisTitle, yAxisTitle)
        
        
        titleAbove = "Distribution of noise mean values (pedestal) from each entry, batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) +", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Mean value (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(pedestal_graph[chan], titleAbove, xAxisTitle, yAxisTitle)
        
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/noise/pedestal_plots/pedestal_"+str(md.getBatchNumber())+"_"+chan+".pdf"
        
        exportGraph(pedestal_graph[chan], canvas_pedestal, fileName)
        #exportROOTFile(pedestal_graph[chan],"noise","pedestal","plots", chan)
        
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/noise/noise_plots/noise_"+str(md.getBatchNumber())+"_"+chan+".pdf"
        
        exportGraph(noise_graph[chan], canvas_noise, fileName)
        #exportROOTFile(noise_graph[chan],"noise","noise","plots", chan)


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



