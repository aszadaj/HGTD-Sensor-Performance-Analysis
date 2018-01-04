import ROOT
import metadata as md
import numpy as np

def producePulseDistributionPlots(peak_values, peak_times, rise_times):

    canvas_peak_values = ROOT.TCanvas("Peak value Distribution", "peak_value")
    canvas_peak_times = ROOT.TCanvas("Peak time Distribution", "peak_time")
    canvas_rise_times = ROOT.TCanvas("Rise time Distribution", "rise_time")

    peak_values_graph = dict()
    peak_times_graph = dict()
    rise_times_graph = dict()
    
    for chan in peak_values.dtype.names:
        
        peak_values_graph[chan] = ROOT.TH1D("Peak value channel "+str(int(chan[-1:])+1), "peak_value" + chan, 1000, 0, 400)
        
        peak_times_graph[chan] = ROOT.TH1D("Peak time channel "+str(int(chan[-1:])+1), "peak_time" + chan, 600, 0, 100)
        
        rise_times_graph[chan] = ROOT.TH1D("Rise time channel "+str(int(chan[-1:])+1), "rise_time" + chan, 600, 0, 1.5)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(peak_values[chan])):
        
            if peak_values[chan][entry] != 0:
                peak_values_graph[chan].Fill(peak_values[chan][entry])
            
            if peak_times[chan][entry] != 0:
                peak_times_graph[chan].Fill(peak_times[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_graph[chan].Fill(rise_times[chan][entry])
    

        typeOfGraph = "peak_value"
        defineAndProduceHistogram(peak_values_graph[chan],canvas_peak_values,typeOfGraph,chan)
        
        typeOfGraph = "peak_time"
        defineAndProduceHistogram(peak_times_graph[chan],canvas_peak_times,typeOfGraph,chan)
        
        typeOfGraph = "rise_time"
        defineAndProduceHistogram(rise_times_graph[chan],canvas_rise_times,typeOfGraph,chan)

# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,chan):

    headTitle = "Distribution of pulse rise times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/pulse/rise_time_plots/rise_time_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    
    
    if typeOfGraph == "peak_value":
    
        headTitle = "Distribution of pulse peak values, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Amplitude (mV)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/pulse/peak_value_plots/peak_value_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    

    elif typeOfGraph == "peak_time":
    
        headTitle = "Distribution of pulse peak times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Time (ns)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/pulse/peak_time_plots/peak_time_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    
  

    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    graphList.SetTitle(headTitle)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)
