import ROOT
import numpy as np

import metadata as md
import data_management as dm

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(100)

def produceTrackingGraphs(peak_values, tracking):
   
    global minEntries
    global chan_index
    global chan
    global canvas
    global batchOrRunNumber
    global sensor_position
    global center_separation_x
    global center_separation_y
    global bins
    
    # Change if data are not concatenated, that is per run number
    batchOrRunNumber = str(md.getBatchNumber())
    
    # Binning resolution and data selection

    bins = 100
    minEntries = 2
    
  
    # Convert pulse data to positive mV values, and x and y positions into mm.
    tracking, peak_values = dm.convertTrackingData(tracking, peak_values)
    
    # Import center positions info for given batch
    sensor_position = dm.importTrackingFile("position")
    center_separation_x = 1
    center_separation_y = 0.75
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    
    channels = peak_values.dtype.names
    #channels = ["chan0"]

    for chan in channels:
        
        chan_index = str(int(chan[-1:]))
        
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
            produceMeanValue2DPlots(peak_values, tracking)
            produceEfficiency2DPlot(peak_values, tracking)


def produceMeanValue2DPlots(peak_values, tracking):
    
    xmin = sensor_position[chan][0][0] - center_separation_x
    xmax = sensor_position[chan][0][0] + center_separation_x
    ymin = sensor_position[chan][0][1] - center_separation_y
    ymax = sensor_position[chan][0][1] + center_separation_y
    xbin = bins
    ybin = bins

    mean_values = dict()
    
    mean_values[chan] = ROOT.TProfile2D("Mean value "+chan,"Mean value channel "+chan, xbin, xmin, xmax, ybin, ymin, ymax)

    # Fill the events, later on remove the bins with less than minEntries-variable
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and peak_values[chan][event] > -md.getPulseAmplitudeCut(chan)*1000:
            mean_values[chan].Fill(tracking['X'][event], tracking['Y'][event], peak_values[chan][event])


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = mean_values[chan].GetBin(i,j)
            num = mean_values[chan].GetBinEntries(bin)

            if 0 < num < minEntries:
                mean_values[chan].SetBinContent(bin, 0)
                mean_values[chan].SetBinEntries(bin, 0)

    # Set the range to avoid plotting overflow and underflow bins
    mean_values[chan].SetAxisRange(xmin+0.05, xmax-0.05, "X")
    mean_values[chan].SetAxisRange(ymin+0.05, ymax-0.05, "Y")

    # Set linear scale (to prevent from having in log scale from TEfficiency
    canvas.SetLogz(0)
    ROOT.gStyle.SetOptStat(1)

    # Print mean value 2D plot
    headTitle = "Pulse amplitude mean value (mV) in each bin, Sep 2017 batch " + batchOrRunNumber +", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_mean_value_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    titles = [headTitle, fileName]
    printTHPlot(mean_values[chan], canvas, titles)

    return np.array([mean_values[chan].GetMean(),mean_values[chan].GetMean(2) ])


def produceEfficiency2DPlot(peak_values, tracking):

    xmin = sensor_position[chan][0][0] - center_separation_x
    xmax = sensor_position[chan][0][0] + center_separation_x
    ymin = sensor_position[chan][0][1] - center_separation_y
    ymax = sensor_position[chan][0][1] + center_separation_y
    xbin = bins
    ybin = bins

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
        if tracking["X"][event] > -9.0 and tracking["Y"][event] > -9.0:
        
            # Total events
            MIMOSA[chan].Fill(tracking["X"][event], tracking["Y"][event], 1)
            
            # Passed events
            if peak_values[chan][event] > -md.getPulseAmplitudeCut(chan)*1000:
                LGAD[chan].Fill(tracking["X"][event], tracking["Y"][event], 1)

    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = MIMOSA[chan].GetBin(i,j)
            num_MIMOSA = MIMOSA[chan].GetBinContent(bin)
            num_LGAD = LGAD[chan].GetBinContent(bin)

            if 0 < num_MIMOSA < minEntries:
                MIMOSA[chan].SetBinContent(bin, 0)
            
            if 0 < num_LGAD < minEntries:
                LGAD[chan].SetBinContent(bin, 0)

    efficiency[chan] = ROOT.TEfficiency(LGAD[chan], MIMOSA[chan])

    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = efficiency[chan].GetGlobalBin(i,j)
            eff = efficiency[chan].GetEfficiency(bin)
            
            if eff != 0:
                inefficiency[chan].SetBinContent(bin, 1-eff)
                
    inefficiency[chan].SetAxisRange(xmin+0.05, xmax-0.05, "X")
    inefficiency[chan].SetAxisRange(ymin+0.05, ymax-0.05, "Y")
    
    # Print graphs without log scale
    canvas.SetLogz(0)
    ROOT.gStyle.SetOptStat(0)

    # Print efficiency plot
    headTitle = "Efficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_efficiency_" + batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTHPlot(efficiency[chan], canvas, titles, True, [xmin, xmax, ymin, ymax])
    
    
#    # Print efficiency profile x plot
#    headTitle = "Projected histogram along X-axis from the efficiency graph, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_efficiency_profile_x_" + batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(efficiency[chan].GetTotalHistogram().ProfileX(), canvas, titles, False, [xmin, xmax, ymin, ymax], True)
#
#    # Print efficiency profile y plot
#    headTitle = "Projected histogram along Y-axis from the efficiency graph, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_efficiency_profile_y_" + batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(efficiency[chan].GetTotalHistogram().ProfileX(), canvas, titles, False, [xmin, xmax, ymin, ymax], True)

    

    # Print inefficiency plot
    headTitle = "Inefficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_inefficiency_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTHPlot(inefficiency[chan], canvas, titles)
    
#    # Print inefficiency profile x plot
#    headTitle = "Projected histogram along X-axis from the inefficiency graph, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_inefficiency_profile_x_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProfileX(), canvas, titles, False, "", True)
#
#    # Print inefficiency profile y plot
#    headTitle = "Projected histogram along Y-axis from the inefficiency graph, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_inefficiency_profile_y_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProfileY(), canvas, titles, False, "", True)

    # Print graphs with log scale

    # Print efficiency plot with log scale
    canvas.SetLogz()

    headTitle = "Efficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_efficiency_" + batchOrRunNumber +"_"+chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
    titles = [headTitle, fileName]
    printTHPlot(efficiency[chan], canvas, titles, True, [xmin, xmax, ymin, ymax])


    # Print inefficiency plot with log scale
    headTitle = "Inefficiency in each bin, Sep 2017 batch " + batchOrRunNumber + ", channel " + chan_index + ", sensor: " + md.getNameOfSensor(chan) + ", bins: " + str(ybin) +", min entries in bin: "+str(minEntries) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/tracking_inefficiency_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
    titles = [headTitle, fileName]
    printTHPlot(inefficiency[chan], canvas, titles)



def printTHPlot(graphList, canvas, titles, efficiency=False, ranges=[], th1=False):
    

    graphList.SetTitle(titles[0])
    
    drawOpt = "COLZ"
    
    if th1:
        drawOpt = ""
    
    graphList.Draw(drawOpt)
    canvas.Update()
    
    if efficiency:
        graphList.GetPaintedHistogram().SetAxisRange(ranges[0]+0.05, ranges[1]-0.05, "X")
        graphList.GetPaintedHistogram().SetAxisRange(ranges[2]+0.05, ranges[3]-0.05, "Y")
        canvas.Update()
    
    canvas.Print(titles[1])
    canvas.Clear()

