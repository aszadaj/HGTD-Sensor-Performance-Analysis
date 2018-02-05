import ROOT
import numpy as np

import metadata as md

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(400)

def produceTrackingGraphs(peak_values, tracking):
   
    global xMin
    global xMax
    global xBins
    
    global yMin
    global yMax
    global yBins
    
    global chan

    xMin = -6
    xMax = 2.0
    xBins = 700
    
    yMin = 10
    yMax = 15
    yBins = xBins
    
    tracking, peak_values = convertTrackingData(tracking, peak_values)
    
    channels = peak_values.dtype.names
    
    

    for chan in channels:
        
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
        
            produce2DPlots(peak_values, tracking)
            produceEfficiencyPlot(peak_values, tracking)


def produce2DPlots(peak_values, tracking):

    chan_index = str(int(chan[-1:]))
    
    canvas = ROOT.TCanvas("Tracking "+chan, "tracking"+chan)
    graph2D = ROOT.TProfile2D("tracking_"+chan,"Tracking channel "+chan_index,xBins,xMin,xMax,yBins,yMin,yMax)

    for index in range(0, len(tracking)):
        if tracking['X'][index] > -9.0 and peak_values[chan][index] != 0.0:
            graph2D.Fill(tracking['X'][index], tracking['Y'][index], peak_values[chan][index])


    # Print original TProfile2D
    headTitle = "Pulse amplitude mean value (mV) in each bin"
    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + "; " + "X position (mm)" + "; " + "Y position (mm)"

    graph2D.SetTitle(title)
    canvas.cd()
    graph2D.Draw("COLZ")
    canvas.Update()
    #canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_"+str(md.getBatchNumber())+"_"+chan + ".pdf")
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_"+str(md.getRunNumber())+"_"+chan + ".pdf")
    canvas.Clear()


def produceEfficiencyPlot(peak_values, tracking):

    chan_index = str(int(chan[-1:]))
    
    canvas = ROOT.TCanvas("Tracking "+chan, "tracking"+chan)
    
    LGAD        = ROOT.TH2F("LGAD_particles_"+chan, "LGAD particles channel "+chan_index, xBins,xMin,xMax,yBins,yMin,yMax)
    MIMOSA      = ROOT.TH2F("tracking_particles_"+chan, "Tracking particles channel "+chan_index, xBins,xMin,xMax,yBins,yMin,yMax)


    # Fill two TH2F objects, where the other is filled if there is a peak value in the event
    for index in range(0, len(tracking)):

        if tracking["X"][index] > -9.0:
            MIMOSA.Fill(tracking["X"][index], tracking["Y"][index], 1)
            if peak_values[chan][index] != 0.0:
                LGAD.Fill(tracking["X"][index], tracking["Y"][index], 1)

    efficiency = ROOT.TEfficiency(LGAD, MIMOSA)

    # Remove bins with less than 3 entries
    for i in range(1, xBins+1):
        for j in range(1, yBins+1):
            bin = efficiency.GetGlobalBin(i,j)
            num = efficiency.GetTotalHistogram().GetBinContent(bin)
            if num < 1:
                efficiency.SetPassedEvents(bin, 0)
                efficiency.SetTotalEvents(bin, 0)


    # Print TEfficiency plot
    headTitle = "Efficiency in each bin, "
    #title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber()) + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    
    title = headTitle + ", Sep 2017 batch " + str(md.getRunNumber()) + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", entries "+str(int(LGAD.GetEntries())) + "; " + "X position (mm)" + "; " + "Y position (mm)"

    efficiency.SetTitle(title)
    canvas.cd()
    efficiency.Draw("COLZ")
    canvas.Update()
    #canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_efficiency_"+str(md.getBatchNumber())+"_"+chan + ".pdf")
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_efficiency_"+str(md.getRunNumber())+"_"+chan + ".pdf")
    canvas.Clear()


def convertTrackingData(tracking, peak_values):

    for dimension in tracking.dtype.names:
        tracking[dimension] = np.multiply(tracking[dimension], 0.001)

    for chan in peak_values.dtype.names:
        peak_values[chan] = np.multiply(peak_values[chan], -1000)

    return tracking, peak_values

