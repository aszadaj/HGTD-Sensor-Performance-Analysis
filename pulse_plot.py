import ROOT
import metadata as md
import numpy as np


def producePulseDistributionPlots(amplitudes, rise_times):

    canvas_amplitude = ROOT.TCanvas("Amplitude Distribution", "amplitude")
    canvas_rise_time = ROOT.TCanvas("Risetime Distribution", "risetime")

    amplitudes_graph = dict()
    rise_times_graph = dict()
    
    for chan in amplitudes.dtype.names:
        
        amplitudes_graph[chan] = ROOT.TH1D("Amplitude channel "+str(int(chan[-1:])+1), "amplitude" + chan,1000,0,400)
        
        #rise_times_graph[chan] = ROOT.TH1D("Rise time channel "+str(int(chan[-1:])+1), "rise_time" + chan,600,0.3,1.5)
        rise_times_graph[chan] = ROOT.TH1D("Rise time channel "+str(int(chan[-1:])+1), "rise_time" + chan,200,0,100)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(amplitudes[chan])):
            #if amplitudes[chan][entry] != 0 and rise_times[chan][entry] != 0:
            #if amplitudes[chan][entry] != 0:
            if amplitudes[chan][entry] != 0:
                amplitudes_graph[chan].Fill(amplitudes[chan][entry])
            if rise_times[chan][entry] != 0:
                rise_times_graph[chan].Fill(rise_times[chan][entry])
    
    
        ### Export ROOT files!! ###
        
        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitudes_graph[chan],canvas_amplitude,typeOfGraph,chan)
        typeOfGraph = "rise_time"
        defineAndProduceHistogram(rise_times_graph[chan],canvas_rise_time,typeOfGraph,chan)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,chan):
  
    headTitle = "Distribution of pulse rise times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/pulse/rise_time_plots/rise_time_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    
    
    if typeOfGraph == "amplitude":
    
        headTitle = "Distribution of pulse amplitudes, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Amplitude (mV)"
        fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/pulse/amplitude_plots/amplitude_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
  

    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    graphList.SetTitle(headTitle)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)
