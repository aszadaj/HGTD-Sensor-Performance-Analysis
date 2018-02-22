import ROOT
import numpy as np

import metadata as md
import data_management as dm

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(400)

def produceTrackingGraphs(peak_values, tracking):
   
    global minEntries
    global chan_index
    global chan
    global canvas
    global batchOrRunNumber
    
    # Change if data are not concatenated, that is per run number
    batchOrRunNumber = str(md.getBatchNumber())
   
    # Chosen start ranges for the approximate position of the MIMOSA
    xmin = -7
    xmax = 5
    ymin = 6
    ymax = 15
    
    # Separation on the final plot
    x_sep = 1.0
    y_sep = 0.8
    scaleGraph = 1.47 # Ratio of y/x on printed graph
    
    # Binning resolution and data selection
    bins = 250
    minEntries = 3
    
    xbin = int(bins*scaleGraph*(2*y_sep))
    ybin = bins
    
    # Convert pulse data to positive mV values, and x and y positions into mm.
    tracking, peak_values = dm.convertTrackingData(tracking, peak_values)
    
    channels = peak_values.dtype.names
    
    #channels = ["chan1"]
    
    canvas = ROOT.TCanvas("Tracking", "tracking")

    for chan in channels:
        
        rangeInfo = [xbin, xmin, xmax, ybin, ymin, ymax]
        chan_index = str(int(chan[-1:]))
        
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
        
            rangeInfo = produceMeanValue2DPlots(peak_values, tracking, rangeInfo, x_sep, y_sep)
            produceEfficiency2DPlot(peak_values, tracking, rangeInfo)


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

    mean_values[chan].SetAxisRange(xmin, xmax, "X")
    mean_values[chan].SetAxisRange(ymin, ymax, "Y")
   
    # Set linear scale (to prevent from having in log scale from TEfficiency
    canvas.SetLogz(0)

    # Print mean value 2D plot
    headTitle = "Pulse amplitude mean value (mV) in each bin, Sep 2017 batch " + batchOrRunNumber +", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_mean_value_"+ batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    titles = [headTitle, fileName]
    printTH2Plot(mean_values[chan], canvas, titles)


    return [xbin, xmin, xmax, ybin, ymin, ymax]


def produceEfficiency2DPlot(peak_values, tracking, rangeInfo):

    [xbin, xmin, xmax, ybin, ymin, ymax] = [i for i in rangeInfo]
    
    LGAD = dict()
    MIMOSA = dict()
    inefficiency = dict()
    efficiency = dict()
    
    # Fill events for which the sensors records a hit
    LGAD[chan]        = ROOT.TH2F("LGAD_particles_"+chan, "LGAD particles channel "+chan_index,xbin,xmin,xmax,ybin,ymin,ymax)
    
    # Fill events for which the tracking notes a hit
    MIMOSA[chan]      = ROOT.TH2F("tracking_particles_"+chan, "Tracking particles channel "+chan_index,xbin,xmin,xmax,ybin,ymin,ymax)
    
    # For a given TEfficiency object, recreate to make it an inefficiency
    inefficiency[chan]      = ROOT.TH2F("Inefficiency_"+chan, "Inefficiency channel "+chan_index,xbin,xmin,xmax,ybin,ymin,ymax)


    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if tracking["X"][event] > -9.0:
            MIMOSA[chan].Fill(tracking["X"][event], tracking["Y"][event], 1)
        
            if peak_values[chan][event] != 0.0:
                LGAD[chan].Fill(tracking["X"][event], tracking["Y"][event], 1)


    efficiency[chan] = ROOT.TEfficiency(LGAD[chan], MIMOSA[chan])

    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = efficiency[chan].GetGlobalBin(i,j)
            num = efficiency[chan].GetTotalHistogram().GetBinContent(bin)
            eff = efficiency[chan].GetEfficiency(bin)
            
            if 0 < num < minEntries:
                efficiency[chan].SetPassedEvents(bin, 0)
                efficiency[chan].SetTotalEvents(bin, 0)
                inefficiency[chan].SetBinContent(bin, 0)
            
            else:
        
                inefficiency[chan].SetBinContent(bin, 1-eff)


    canvas.SetLogz()

    # Print efficiency plot
    headTitle = "Efficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_efficiency_" + batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTH2Plot(efficiency[chan], canvas, titles)

    # Print inefficiency plot
    headTitle = "Inefficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_inefficiency_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTH2Plot(inefficiency[chan], canvas, titles)



def printTH2Plot(graphList, canvas, titles):

    graphList.SetTitle(titles[0])
    graphList.Draw("COLZ")
    canvas.Update()
    canvas.Print(titles[1])
    canvas.Clear()

