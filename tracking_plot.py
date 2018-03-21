import ROOT
import numpy as np

import metadata as md
import data_management as dm

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(300)

def produceTrackingGraphs(peak_values, tracking):
   
    global minEntries
    global chan_index
    global chan
    global canvas
    global batchOrRunNumber
    global sensor_position
    global sep_x
    global sep_y
    
    # Change if data are not concatenated, that is per run number
    batchOrRunNumber = str(md.getBatchNumber())
    
    # Data selection
    minEntries = 3
    
    # Convert pulse data to positive mV values, and x and y positions into mm.
    tracking, peak_values = dm.convertTrackingData(tracking, peak_values)
    
    # Import center positions info for given batch
    sensor_position = dm.importTrackingFile("position")
    sep_x = 0.7
    sep_y = 0.7
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    
    channels = peak_values.dtype.names
    #channels = ["chan0"]

    for chan in channels:
        
        chan_index = str(int(chan[-1:]))
        
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
            produceMeanValue2DPlots(peak_values, tracking)
            produceEfficiency2DPlot(peak_values, tracking)


def produceMeanValue2DPlots(peak_values, tracking):

    pos_x = sensor_position[chan][0][0]
    pos_y = sensor_position[chan][0][1]

    # Telescope bin size in mm
    bin_size = 18.5 * 0.001
    
    # For data with 1 run number
    #bin_size *= 2
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)

    mean_values = dict()
    
    mean_values[chan] = ROOT.TProfile2D("Mean value "+chan,"Mean value channel "+chan, xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)

    # Fill the events, later on remove the bins with less than minEntries-variable
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and peak_values[chan][event] > -md.getPulseAmplitudeCut(chan)*1000:
            mean_values[chan].Fill(tracking['X'][event] - pos_x, tracking['Y'][event] - pos_y, peak_values[chan][event])


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = mean_values[chan].GetBin(i,j)
            num = mean_values[chan].GetBinEntries(bin)

            if 0 < num < minEntries:
                mean_values[chan].SetBinContent(bin, 0)
                mean_values[chan].SetBinEntries(bin, 0)

    mean_values[chan].ResetStats()

    # Set the range to avoid plotting overflow and underflow bins
    mean_values[chan].SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    mean_values[chan].SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")
    mean_values[chan].SetAxisRange(-md.getPulseAmplitudeCut(chan)*1000, mean_values[chan].GetMaximum(), "Z")
    mean_values[chan].SetNdivisions(10, "Z")

    # Set linear scale (to prevent from having in log scale from TEfficiency
    canvas.SetLogz(0)
    canvas.SetRightMargin(0.14)
    ROOT.gStyle.SetOptStat(0)



    # Print mean value 2D plot
    headTitle = "Averaged maximal pulse amplitude in each bin " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber +"; X (mm) ; Y (mm) ; V (mV)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/mean_value/tracking_mean_value_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTHPlot(mean_values[chan], canvas, titles)


def produceEfficiency2DPlot(peak_values, tracking):

    pos_x = sensor_position[chan][0][0]
    pos_y = sensor_position[chan][0][1]

    # Telescope bin size in mm
    bin_size = 18.5 * 0.001
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)

    LGAD = dict()
    MIMOSA = dict()
    inefficiency = dict()
    efficiency = dict()
    
    # Fill events for which the sensors records a hit
    LGAD[chan]         = ROOT.TH2F("LGAD_particles_"+chan, "LGAD particles channel "+chan_index,xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA[chan]       = ROOT.TH2F("tracking_particles_"+chan, "Tracking particles channel "+chan_index,xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # For a given TEfficiency object, recreate to make it an inefficiency
    inefficiency[chan] = ROOT.TH2F("Inefficiency_"+chan, "Inefficiency channel "+chan_index,xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    

    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if tracking["X"][event] > -9.0 and tracking["Y"][event] > -9.0:
        
            # Total events
            MIMOSA[chan].Fill(tracking["X"][event] - pos_x, tracking["Y"][event] - pos_y, 1)
            
            # Passed events
            if peak_values[chan][event] > -md.getPulseAmplitudeCut(chan)*1000:
                LGAD[chan].Fill(tracking["X"][event] - pos_x, tracking["Y"][event] - pos_y, 1)
        


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = MIMOSA[chan].GetBin(i,j)
            num_MIMOSA = MIMOSA[chan].GetBinContent(bin)
            num_LGAD = LGAD[chan].GetBinContent(bin)
            
            if 0 < num_LGAD < minEntries:
                LGAD[chan].SetBinContent(bin, 0)
                MIMOSA[chan].SetBinContent(bin, 0)


    efficiency[chan] = ROOT.TEfficiency(LGAD[chan], MIMOSA[chan])

    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = efficiency[chan].GetGlobalBin(i,j)
            eff = efficiency[chan].GetEfficiency(bin)
            
            if eff != 0 and eff != 1:
                inefficiency[chan].SetBinContent(bin, 1-eff)
            
            elif eff == 1:
                inefficiency[chan].SetBinContent(bin, 0.001)


    efficiency[chan].GetPassedHistogram().SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    efficiency[chan].GetPassedHistogram().SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")

    efficiency[chan].GetTotalHistogram().SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    efficiency[chan].GetTotalHistogram().SetAxisRange(-sep_x+0.05, sep_x-0.05, "Y")
    
    inefficiency[chan].SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    inefficiency[chan].SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")
    
    
    
    ### LINEAR SCALE ###
    canvas.SetLogz(0)
    canvas.SetRightMargin(0.14)


    # EFFICIENCY PLOTS #
    
    headTitle = "Efficiency in each bin " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Y (mm) ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTHPlot(efficiency[chan], canvas, titles, True)
    
    
    # Restrict range of TH2 object to plot projection x and y
#    distance_from_center = 0.2
#
#    projection_xmin = -distance_from_center
#    projection_xmax = distance_from_center
#
#    projection_ymin = -distance_from_center
#    projection_ymax = distance_from_center
#
#    efficiency_copy = efficiency[chan].GetPaintedHistogram()
#
#
#    xbin_low_proj = efficiency_copy.GetXaxis().FindBin(projection_xmin)
#    xbin_high_proj = efficiency_copy.GetXaxis().FindBin(projection_xmax)
#
#    ybin_low_proj = efficiency_copy.GetYaxis().FindBin(projection_ymin)
#    ybin_high_proj = efficiency_copy.GetYaxis().FindBin(projection_ymax)

    
    

#    # PROJECTION PLOTS #
#
#    profileXPlot = efficiency_copy.ProjectionX("projx", ybin_low_proj, ybin_high_proj, "e")
#    profileYPlot = efficiency_copy.ProjectionY("projy", xbin_low_proj, xbin_high_proj, "e")
#
#
#
#    # Print efficiency profile x plot linear scale
#    headTitle = "Projected histogram along X-axis from the efficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Efficiency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_proj_x_" + batchOrRunNumber +"_" +chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(profileXPlot, canvas, titles, False, True, True)
#
#    # Print efficiency profile y plot linear scale
#    headTitle = "Projected histogram along Y-axis from the efficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; Y (mm) ; Efficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_proj_y_" + batchOrRunNumber +"_" +chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(profileYPlot, canvas, titles, False, True, True)

    
    
    ### INEFFICIENCY PLOTS ###

    # Print inefficiency plot linear scale
    headTitle = "Inefficiency in each bin " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Y (mm) ; Inefficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printTHPlot(inefficiency[chan], canvas, titles, False, True)
    
    
    
    
#    # Print inefficiency profile x plot linear scale
#    headTitle = "Projected histogram along X-axis from the inefficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Inefficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_proj_x_"+ batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProfileX(), canvas, titles, False, True, True)
#
#    # Print inefficiency profile y plot linear scale
#    headTitle = "Projected histogram along Y-axis from the inefficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; Y (mm) ; Inefficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_proj_y_"+ batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProfileY(), canvas, titles, False, True, True)



#    ### LOG SCALE ###
#    canvas.SetLogz()
#
#
#    # EFFICIENCY PLOTS #
#
#    # Print efficiency plot log scale
#    headTitle = "Efficiency in each bin " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Y (mm) ; Efficiency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + batchOrRunNumber +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(efficiency[chan], canvas, titles, True)

    
    
    
#    # Print efficiency projection x plot log scale
#    headTitle = "Projected histogram along X-axis from the efficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Efficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_proj_x_" + batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(efficiency[chan].GetPassedHistogram().ProjectionX(), canvas, titles, False, True, True)
#
#    # Print efficiency log scale projection y plot
#    headTitle = "Projected histogram along Y-axis from the efficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; Y (mm) ; Efficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_proj_y_" + batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(efficiency[chan].GetPassedHistogram().ProjectionY(), canvas, titles, False, True, True)


#    ## INEFFICIENCY PLOTS ##
#
#    # Print inefficiency plot log scale
#    headTitle = "Inefficiency in each bin " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Y (mm) ; Efficiency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan], canvas, titles)

#
#    # Print inefficiency projection x plot log scale
#    headTitle = "Projected histogram along X-axis from the inefficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; X (mm) ; Inefficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_proj_x_" + batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProjectionX(), canvas, titles, False, True, True)
#
#
#    # Print inefficiency projection y plot log scale
#    headTitle = "Projected histogram along Y-axis from the inefficiency graph " + md.getNameOfSensor(chan) + " B" + batchOrRunNumber + "; Y (mm) ; Inefficency (%)"
#    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_proj_y_" + batchOrRunNumber +"_" + chan + "_"+str(md.getNameOfSensor(chan))+"_log.pdf"
#    titles = [headTitle, fileName]
#    printTHPlot(inefficiency[chan].ProjectionY(), canvas, titles, False, True, True)



def printTHPlot(graphList, canvas, titles, efficiency=False, th1=False, proj=False):
    
    graphList.SetTitle(titles[0])
    
    drawOpt = "COLZ"
    
    if th1:
        drawOpt = ""
    
    graphList.Draw(drawOpt)
    
    canvas.Update()
    
    if efficiency:
        graphList.GetPaintedHistogram().Scale(100)
        
        canvas.Update()
        
        #graphList.GetPaintedHistogram().SetAxisRange(80, 100, "Z")
        graphList.GetPaintedHistogram().SetNdivisions(10, "Z")
        graphList.GetPaintedHistogram().SetTitle(titles[0])
        graphList.GetPaintedHistogram().Draw(drawOpt)

    elif th1:
        graphList.Scale(100)
        graphList.SetNdivisions(10, "Z")


    canvas.Update()

    # Export PDF
    canvas.Print(titles[1])
    
    # Export ROOT TH2 Histogram
    rootDestination = titles[1].replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDestination = rootDestination.replace(".pdf", ".root")
    fileObject = ROOT.TFile(rootDestination, "RECREATE")
    fileObject.WriteTObject(graphList)
    fileObject.Close()

    canvas.Clear()

