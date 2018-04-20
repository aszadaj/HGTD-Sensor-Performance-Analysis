import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(400)

def produceTrackingGraphs(peak_values, tracking):
   
    global minEntries
    global chan_index
    global chan
    global canvas
   
    # Chosen start ranges for the approximate position of the MIMOSA
    xmin = -7
    xmax = 7
    ymin = 5
    ymax = 16
    
    # How much to separate on the scaling
    x_sep = 1.0
    y_sep = 0.8
    scaleGraph = 1.47 # Ratio of y/x on printed graph
    
    # Binning resolution and data selection
    bins = 80
    minEntries = 3
    
    
    xbin = int(bins*scaleGraph*(2*y_sep))
    ybin = bins
    
    # Convert pulse data to positive mV values, and x and y positions into mm.
    tracking, peak_values = dm.convertTrackingData(tracking, peak_values)
    
    channels = peak_values.dtype.names
    
    #channels = ["chan1"]
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    
    position = dm.createCenterPositionArray()

    for chan in channels:
        
        rangeInfo = [xbin, xmin, xmax, ybin, ymin, ymax]
        chan_index = str(int(chan[-1:]))
        
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
        
            position[chan][0] = produceMeanValue2DPlots(peak_values, tracking, rangeInfo, x_sep, y_sep)

    dm.exportTrackingData(position)

def produceMeanValue2DPlots(peak_values, tracking, rangeInfo, x_sep, y_sep):
    [xbin, xmin, xmax, ybin, ymin, ymax] = [i for i in rangeInfo]
    
    mean_values = dict()
    
    mean_values[chan] = ROOT.TProfile2D("Mean value "+chan,"Mean value channel "+chan, xbin, xmin, xmax, ybin, ymin, ymax)

    # Fill the events, later on remove the bins with less than minEntries-variable
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and peak_values[chan][event] != 0:
            mean_values[chan].Fill(tracking['X'][event], tracking['Y'][event], peak_values[chan][event])


    # Remove bins with less than some entries
    for bin in range(1, (xbin*ybin)+1):
        num = mean_values[chan].GetBinEntries(bin)

        if 0 < num < minEntries:
            mean_values[chan].SetBinContent(bin, 0)
            mean_values[chan].SetBinEntries(bin, 0)

    # Rescale bins and set new axis (this is used for both types of graphs)
    xbin = int(xbin/(2*x_sep))
    ybin = int(ybin/(2*y_sep))
    xmin = mean_values[chan].GetMean() - x_sep
    xmax = mean_values[chan].GetMean() + x_sep
    ymin = mean_values[chan].GetMean(2) - y_sep
    ymax = mean_values[chan].GetMean(2) + y_sep
    
    titles = [chan, chan+".pdf"]
    printTH2Plot(mean_values[chan], canvas, titles)

    #mean_values[chan].SetAxisRange(xmin, xmax, "X")
    #mean_values[chan].SetAxisRange(ymin, ymax, "Y")
   
    # Set linear scale (to prevent from having in log scale from TEfficiency
    canvas.SetLogz(0)

    position = np.array([mean_values[chan].GetMean(), mean_values[chan].GetMean(2)])
    
    return position


def printTH2Plot(graphList, canvas, titles):

    graphList.SetTitle(titles[0])
    graphList.Draw("COLZ")
    canvas.Update()
    canvas.Print(titles[1])
    canvas.Clear()

