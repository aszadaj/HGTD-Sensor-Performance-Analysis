import ROOT
import numpy as np

import metadata as md
import data_management as dm

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(300)

def produceTrackingGraphs(peak_values, tracking, time_difference_peak, time_difference_rise_time_ref):
   
    global minEntries
    global canvas
    global bin_size
    global sep_x
    global sep_y
    
    # Data selection
    minEntries = 3
    
    # Convert pulse data to positive mV values, and x and y positions into mm.
    tracking, peak_values = dm.convertTrackingData(tracking, peak_values)
    
    # Import center positions info for given batch
    position = dm.importTrackingFile("position")
    sep_x = 0.9
    sep_y = 0.7
    
    # Telescope bin size in mm
    bin_size = 18.5 * 0.001
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    
    channels = peak_values.dtype.names
    
    # In case there are arrays in batch, produce seperately array plots
    #produceArrayPlots(peak_values, tracking, position)
    
    channels = ["chan0"]

    for chan in channels:

        if chan != md.getChannelNameForSensor("SiPM-AFP") and md.getNameOfSensor(chan) != "W4-S215" and md.getNameOfSensor(chan) != "W4-S204_6e14":
            pos_x = position[chan][0][0]
            pos_y = position[chan][0][1]

            #produceMeanValue2DPlots(peak_values[chan], tracking, time_difference_peak[chan], time_difference_rise_time_ref[chan],  pos_x, pos_y, chan)
            produceEfficiency2DPlot(peak_values[chan], tracking, pos_x, pos_y, chan)


def produceMeanValue2DPlots(peak_values, tracking, time_difference_peak, time_difference_rise_time_ref, pos_x, pos_y, chan, array_pad=False):


    sep_x, sep_y, bin_size = getSepGlobVar()

    if array_pad:
        sep_x *= 1.9
        sep_y *= 1.9
    
    bin_size *= 1.5

    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    mean_values = dict()
    timing_resolution_peak = dict()
    timing_resolution_rise_time_ref = dict()

    timing_resolution_peak_copy = dict()
    timing_resolution_rise_time_ref_copy = dict()
    

    mean_values[chan] = ROOT.TProfile2D("Mean value","Mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)

    timing_resolution_peak[chan] = ROOT.TProfile2D("Timing resolution peak", "timing resolution peak temp", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y, "s")
    timing_resolution_rise_time_ref[chan] = ROOT.TProfile2D("Timing resolution rise time ref temp", "timing resolution rtref", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y, "s")

    timing_resolution_peak_copy[chan] = ROOT.TH2F("Timing resolution peak copy", "timing resolution peak", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    timing_resolution_rise_time_ref_copy[chan] = ROOT.TH2F("Timing resolution rise time ref", "timing resolution rtref", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)

    # Fill the events, later on remove the bins with less than minEntries-variable
    for event in range(0, len(tracking)):
    
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
            mean_values[chan].Fill(tracking['X'][event] - pos_x, tracking['Y'][event] - pos_y, peak_values[event])
        
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and time_difference_peak[event] != 0:

            timing_resolution_peak[chan].Fill(tracking['X'][event] - pos_x, tracking['Y'][event] - pos_y, time_difference_peak[event])
        
        if tracking['X'][event] > -9.0 and tracking['Y'][event] > -9.0 and time_difference_rise_time_ref[event] != 0:

            timing_resolution_rise_time_ref[chan].Fill(tracking['X'][event] - pos_x, tracking['Y'][event] - pos_y, time_difference_rise_time_ref[event])


    sigma_sipm = 16.14

    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = mean_values[chan].GetBin(i,j)
            num_mean = mean_values[chan].GetBinEntries(bin)
            num_time_peak = timing_resolution_peak[chan].GetBinEntries(bin)
            num_time_rtref = timing_resolution_rise_time_ref[chan].GetBinEntries(bin)
            

            if 0 < num_mean < minEntries:
                mean_values[chan].SetBinContent(bin, 0)
                mean_values[chan].SetBinEntries(bin, 0)

            if 0 < num_time_peak < minEntries:
                timing_resolution_peak[chan].SetBinContent(bin, 0)
                timing_resolution_peak[chan].SetBinEntries(bin, 0)
            
            elif num_time_peak > 20:
                sigma_dut_conv = timing_resolution_peak[chan].GetBinError(bin)*1000
                if sigma_dut_conv != 0:
                    sigma_dut = np.sqrt(sigma_dut_conv**2 - sigma_sipm**2)
                    if not np.isnan(sigma_dut):
                        timing_resolution_peak_copy[chan].SetBinContent(bin, sigma_dut)

            if 0 < num_time_rtref < minEntries:
                timing_resolution_rise_time_ref[chan].SetBinContent(bin, 0)
                timing_resolution_rise_time_ref[chan].SetBinEntries(bin, 0)
            
            elif num_time_rtref > 20:
                sigma_dut_conv = timing_resolution_rise_time_ref[chan].GetBinError(bin)*1000
                if sigma_dut_conv != 0:
                    sigma_dut = np.sqrt(sigma_dut_conv**2 - sigma_sipm**2)
                    if not np.isnan(sigma_dut):
                        timing_resolution_rise_time_ref_copy[chan].SetBinContent(bin, sigma_dut)


    mean_values[chan].ResetStats()

    # Set the range to avoid plotting overflow and underflow bins
    mean_values[chan].SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    mean_values[chan].SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")
    mean_values[chan].SetAxisRange(-md.getPulseAmplitudeCut(chan)*1000, mean_values[chan].GetMaximum(), "Z")
    mean_values[chan].SetNdivisions(10, "Z")
    
    # Set the range to avoid plotting overflow and underflow bins
    timing_resolution_peak_copy[chan].SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    timing_resolution_peak_copy[chan].SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")
    timing_resolution_peak_copy[chan].SetAxisRange(0, 100, "Z")
    
    # Set the range to avoid plotting overflow and underflow bins
    timing_resolution_rise_time_ref_copy[chan].SetAxisRange(-sep_x+0.05, sep_x-0.05, "X")
    timing_resolution_rise_time_ref_copy[chan].SetAxisRange(-sep_y+0.05, sep_y-0.05, "Y")
    timing_resolution_rise_time_ref_copy[chan].SetAxisRange(0, 100, "Z")
    
    
    # Set linear scale (to prevent from having in log scale from TEfficiency
    canvas.SetLogz(0)
    canvas.SetRightMargin(0.14)
    ROOT.gStyle.SetOptStat(0)



    # Print mean value 2D plot
    headTitle = "Averaged pulse amplitude in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; V [mV]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/mean_value/tracking_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    
    titles = [headTitle, fileName]
    printTHPlot(mean_values[chan], titles)


    # Print time resolution mean values

    # Print time resolution peak reference
    headTitle = "Time resolution (peak ref) in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; \sigma_t [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_peak_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName]
    printTHPlot(timing_resolution_peak_copy[chan], titles)


    # Print time resolution rise time ref
    headTitle = "Time resolution (rise time ref) in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; \sigma_t [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_rise_time_ref_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName]
    printTHPlot(timing_resolution_rise_time_ref_copy[chan], titles)


def produceEfficiency2DPlot(peak_values, tracking, pos_x, pos_y, chan, array_pad=False):

    sep_x, sep_y, bin_size = getSepGlobVar()

    if array_pad:
        sep_x *= 1.9
        sep_y *= 1.9        #bin_size *= 1.5

    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    LGAD = dict()
    MIMOSA = dict()
    efficiency = dict()
    inefficiency = dict()
    efficiency_projectionX = dict()
    efficiency_projectionY = dict()
    
    
    # Fill events for which the sensors records a hit
    LGAD[chan]         = ROOT.TH2F("LGAD[chan]_particles", "LGAD[chan] particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA[chan]       = ROOT.TH2F("tracking_particles", "Tracking particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # For a given TEfficiency object, recreate to make it an inefficiency
    inefficiency[chan] = ROOT.TH2F("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Projection X of efficiency
    efficiency_projectionX[chan] = ROOT.TProfile("Projection X plot", "projection X", xbin,-sep_x,sep_x)
    
    # Projection Y of efficiency
    efficiency_projectionY[chan] = ROOT.TProfile("Projection Y plot", "projection X", ybin,-sep_y,sep_y)
    
    
    # Fill MIMOSA[chan] and LGAD[chan] (TH2 objects)
    for event in range(0, len(tracking)):
        if tracking["X"][event] > -9.0 and tracking["Y"][event] > -9.0:
        
            # Total events
            MIMOSA[chan].Fill(tracking["X"][event] - pos_x, tracking["Y"][event] - pos_y, 1)
            
            # Passed events
            if peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
                LGAD[chan].Fill(tracking["X"][event] - pos_x, tracking["Y"][event] - pos_y, 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = MIMOSA[chan].GetBin(i,j)
            num_LGAD = LGAD[chan].GetBinContent(bin)
            
            if 0 < num_LGAD < minEntries:
                LGAD[chan].SetBinContent(bin, 0)
                MIMOSA[chan].SetBinContent(bin, 0)


    bin_low_x = LGAD[chan].GetXaxis().FindBin(-0.3)
    bin_high_x = LGAD[chan].GetXaxis().FindBin(0.3)

    bin_low_y = LGAD[chan].GetYaxis().FindBin(-0.3)
    bin_high_y = LGAD[chan].GetYaxis().FindBin(0.3)

    efficiency[chan] = ROOT.TEfficiency(LGAD[chan], MIMOSA[chan])

    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = efficiency[chan].GetGlobalBin(i,j)
            eff = efficiency[chan].GetEfficiency(bin)
            
            if eff != 0 and eff != 1:
                
                # The factor 4 is to compensate 4 times the tracking info
                if array_pad:
                    inefficiency[chan].SetBinContent(bin, 1-eff*4)
        
                else:
                    inefficiency[chan].SetBinContent(bin, 1-eff)


            elif eff == 1:
                inefficiency[chan].SetBinContent(bin, 0.001)
            
            if bin_low_x <= i <= bin_high_x:
                y_pos = LGAD[chan].GetYaxis().GetBinCenter(j)
                efficiency_projectionY[chan].Fill(y_pos, eff*100)
            
            if bin_low_y <= j <= bin_high_y:
                x_pos = LGAD[chan].GetXaxis().GetBinCenter(i)
                efficiency_projectionX[chan].Fill(x_pos, eff*100)
                
             
 
    
    
    # Print projection X plot
    headTitle = "Projection along x-axis of efficiency plot " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; X [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printProjectionPlot(efficiency_projectionX[chan], titles)
    
    # Print projection Y plot
    headTitle = "Projection along y-axis of efficiency plot " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; Y [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionY_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printProjectionPlot(efficiency_projectionY[chan], titles)
    
    
   


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
    
    headTitle = "Efficiency in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; X [mm] ; Y [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName]

    printTHPlot(efficiency[chan], titles, True, False, array_pad)


    ### INEFFICIENCY PLOTS ###

    # Print inefficiency plot linear scale
    headTitle = "Inefficiency in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; X [mm] ; Y [mm] ; Inefficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName]
    printTHPlot(inefficiency[chan], titles, False, True, array_pad)
    


def produceArrayPlots(peak_values, tracking, position):


    # W4-S215 22 C
    if int(md.getBatchNumber()/100) == 1:

        # Concatenate max amplitude value info for each array sensor
        peak_values_array = np.concatenate((peak_values["chan4"], peak_values["chan5"], peak_values["chan6"], peak_values["chan7"]), axis=0)
        tracking_array = np.concatenate((tracking, tracking, tracking, tracking), axis=0)
        
        # Calculate mean position from position of each array sensor
        array_pos_x = (position["chan4"][0][0] + position["chan5"][0][0] + position["chan6"][0][0] + position["chan7"][0][0])/4
        array_pos_y = (position["chan4"][0][1] + position["chan5"][0][1] + position["chan6"][0][1] + position["chan7"][0][1])/4

        produceMeanValue2DPlots(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan4", True)
        produceEfficiency2DPlot(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan4", True)

    # W4-S215 22 C
    elif int(md.getBatchNumber()/100) == 2:

        # Concatenate max amplitude value info for each array sensor
        peak_values_array = np.concatenate((peak_values["chan3"], peak_values["chan5"], peak_values["chan6"], peak_values["chan7"]), axis=0)
        tracking_array = np.concatenate((tracking, tracking, tracking, tracking), axis=0)
        
        # Calculate mean position from position of each array sensor
        array_pos_x = (position["chan3"][0][0] + position["chan5"][0][0] + position["chan6"][0][0] + position["chan7"][0][0])/4
        array_pos_y = (position["chan3"][0][1] + position["chan5"][0][1] + position["chan6"][0][1] + position["chan7"][0][1])/4

        produceMeanValue2DPlots(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan3", True)
        produceEfficiency2DPlot(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan3", True)

    # W4-S215 -30 C
    elif int(md.getBatchNumber()/100) == 4:

        # Concatenate max amplitude value info for each array sensor
        peak_values_array = np.concatenate((peak_values["chan1"], peak_values["chan5"], peak_values["chan6"], peak_values["chan7"]), axis=0)
        tracking_array = np.concatenate((tracking, tracking, tracking, tracking), axis=0)
        
        # Calculate mean position from position of each array sensor
        array_pos_x = (position["chan1"][0][0] + position["chan5"][0][0] + position["chan6"][0][0] + position["chan7"][0][0])/4
        array_pos_y = (position["chan1"][0][1] + position["chan5"][0][1] + position["chan6"][0][1] + position["chan7"][0][1])/4


        produceMeanValue2DPlots(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan1", True)
        produceEfficiency2DPlot(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan1", True)

    # W4-S204_6e14 -40 C
    elif int(md.getBatchNumber()/100) == 5 or int(md.getBatchNumber()/100) == 7:

        # Concatenate max amplitude value info for each array sensor
        peak_values_array = np.concatenate((peak_values["chan5"], peak_values["chan6"], peak_values["chan7"]), axis=0)
        tracking_array = np.concatenate((tracking, tracking, tracking), axis=0)
        
        # Calculate mean position from position of each array sensor
        array_pos_x = (position["chan5"][0][0] + position["chan6"][0][0] + position["chan7"][0][0])/3
        array_pos_y = (position["chan5"][0][1] + position["chan6"][0][1] + position["chan7"][0][1])/3


        produceMeanValue2DPlots(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan5", True)
        produceEfficiency2DPlot(peak_values_array, tracking_array, array_pos_x, array_pos_y, "chan5", True)


def printTHPlot(graphList, titles, efficiency=False, inefficiency=False, array_pad=False):
    
    graphList.SetTitle(titles[0])
    graphList.Draw("COLZ")
    canvas.Update()
    
    if efficiency:
    
        if array_pad:
            graphList.GetPaintedHistogram().Scale(4)


        graphList.GetPaintedHistogram().Scale(100)
        graphList.GetPaintedHistogram().SetAxisRange(0, 100, "Z")
        graphList.GetPaintedHistogram().SetNdivisions(11, "Z")
        graphList.GetPaintedHistogram().SetTitle(titles[0])
        graphList.GetPaintedHistogram().Draw("COLZ")
        graphList.GetPaintedHistogram().SetStats(1)
        graphList.GetPaintedHistogram().SetEntries(graphList.GetPassedHistogram().GetEntries())
        ROOT.gStyle.SetOptStat(1000000011)
        stats_box = graphList.GetPaintedHistogram().GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.9)
        stats_box.SetY2NDC(0.8)
        stats_box.SetOptStat(1000000011)
        
        proj_line_selection_up = ROOT.TLine(-0.6, 0.3, 0.6, 0.3)
        proj_line_selection_down = ROOT.TLine(-0.6, -0.3, 0.6, -0.3)
        proj_line_selection_up.Draw("same")
        proj_line_selection_down.Draw("same")
        


    elif inefficiency:
        
        graphList.Scale(100)
        graphList.SetAxisRange(0, 10, "Z")
        graphList.SetNdivisions(11, "Z")
        graphList.SetTitle(titles[0])
        graphList.SetStats(1)
        ROOT.gStyle.SetOptStat(1000000011)
        stats_box = graphList.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.9)
        stats_box.SetY2NDC(0.8)
        stats_box.SetOptStat(1000000011)



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

def printProjectionPlot(graphList, titles):

    graphList.SetTitle(titles[0])
    graphList.SetStats(1)
    graphList.Draw()
    canvas.Update()

    # Export PDF
    canvas.Print(titles[1])
    

    canvas.Clear()



def getSepGlobVar():

    return sep_x, sep_y, bin_size
