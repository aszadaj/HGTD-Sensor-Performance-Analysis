import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(255)


# The function receives two arrays, for a specific batch. They are structured as
# data[event][chan], where event spans along all run files. Example for B306 the max event is
# 11 files * 200 000 = 2 200 000 events

def produceTrackingGraphs(data_tracking, data_peak_value):
   
    global xMin
    global xMax
    global xBins
    global yMin
    global yMax
    global yBins
    global chan
    global chan_index
    global data
    global peak_value
    global canvas
    
    xMin = -6
    xMax = 2.0
    xBins = 800
    yMin = 10
    yMax = 15
    yBins = 800
    
    chan_index = str(int(chan[-1:]))
    
    # Convert the amplitude values to positive mV values
    for chan in data_peak_value.dtype.names:
        data_peak_value[chan] = np.multiply(data_peak_value[chan], -1000)

    
    data = data_tracking
    peak_value = data_peak_value

    canvas = ROOT.TCanvas("tracking", "tracking")
    channels = peak_value.dtype.names
    
    #channels = ["chan0"]
    
    for chan in channels:
    
        # 1. Shows the mean amplitude in each filled bin (with or without conditions)
        # 2. Shows efficiency between tracking data and amplitude data
        produce2DPlots()
        produceTEfficiencyPlot()


def produce2DPlots():

    graphOrignal = ROOT.TProfile2D("tracking_"+chan,"Tracking channel "+chan_index,xBins,xMin,xMax,yBins,yMin,yMax)

    # Original mean value TProfile2D
    for index in range(0, len(data)):
        if data['X'][index] > -9.0 and peak_value[chan][index] != 0.0:
            graphOrignal.Fill(data['X'][index], data['Y'][index], peak_value[chan][index])


    # Print original TProfile2D
    headTitle = "Pulse amplitude mean value (mV) in each bin"
    fileName = ".pdf"
    produceTH2Plot(graphOrignal, headTitle, fileName)


    del graphOrignal


def produceTEfficiencyPlot():
    
    efficiencyGraph  = ROOT.TEfficiency("Efficiency_particles_"+chan, "Effciency particles channel "+chan_index, xBins,xMin,xMax,yBins,yMin,yMax)
    LGADGraph        = ROOT.TProfile2D("LGAD_particles_"+chan, "LGAD particles channel "+chan_index, xBins,xMin,xMax,yBins,yMin,yMax)
    MIMOSAGraph      = ROOT.TProfile2D("tracking_particles_"+chan, "Tracking particles channel "+chan_index, xBins,xMin,xMax,yBins,yMin,yMax)
    

    # Original TEfficiency, efficiency graph
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
        
            MIMOSAHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)
            efficiencyOrig.Fill(peak_value[chan][index], data['X'][index], data['Y'][index])
            
            if peak_value[chan][index] > 0.0:
                LGADHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)

    LGADNoHitsOrig = LGADHitsOrig.Clone()
    
    # Original TEfficiency, inefficiency graph
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
            MIMOSAHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)
            if peak_value[chan][index] == 0.0:
                LGADNoHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)


    # Original efficiency graph
    headTitle = "Efficiency of hit particles in each bin"
    fileName = "_eff.pdf"
    #efficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(efficiencyOrig, headTitle, fileName)
    
    
    # Original inefficiency graph
    inEfficiencyOrig = ROOT.TEfficiency(LGADNoHitsOrig, MIMOSAHitsOrig)
    headTitle = "Infficiency of hit particles in each bin"
    fileName = "_ineff.pdf"
    #efficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(inEfficiencyOrig, headTitle, fileName)



def produceTH1MeanPlot(graphTH2):

    graphTH1 = ROOT.TH1F("distribution_"+chan+"_histogram","Mean value distribution "+chan_index,200,0,400)


    for bin in range(0, int(graphTH2.GetSize())):
        error = graphTH2.GetBinError(bin)
        if error != 0.0:
            meanVal = graphTH2.GetBinContent(bin)
            graphTH1.Fill(meanVal)
    

    headTitle = "Mean amplitude value distribution from each bin (mV)"
    fileName = "_hist.pdf"
    produceTH1Plot(graphTH1, headTitle, fileName)

    del graphTH1


def produceTH1Plot(graph, headTitle, fileName):

    title = headTitle + ", Sep 2017 batch " + md.getBatchNumber()+", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + "; " + "Mean amplitude value per bin" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_"+md.getBatchNumber()+"_"+chan + fileName)
    canvas.Clear()



def produceTH2Plot(graph, headTitle, fileName):
    
    title = headTitle + ", Sep 2017 batch " + md.getBatchNumber()+", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_"+md.getBatchNumber()+"_"chan + fileName)
    canvas.Clear



