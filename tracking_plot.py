import ROOT
import numpy as np

import metadata as md

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(255)

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
    xBins = 800
    
    yMin = 10
    yMax = 15
    yBins = 800
    
    tracking, peak_values = convertTrackingData(tracking, peak_values)
    
    channels = peak_values.dtype.names

    for chan in channels:

        produce2DPlots(peak_values, tracking)


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
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/tracking/tracking_"+str(md.getBatchNumber())+"_"+chan + ".pdf")
    canvas.Clear()

def convertTrackingData(tracking, peak_values):

    for dimension in tracking.dtype.names:
        tracking[dimension] = np.multiply(tracking[dimension], 0.001)

    for chan in peak_values.dtype.names:
        peak_values[chan] = np.multiply(peak_values[chan], -1000)

    return tracking, peak_values

