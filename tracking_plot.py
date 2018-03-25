import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import timing_calculations as t_calc

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
    peak_values = dm.convertPulseData(peak_values)
    
    # Import center positions info for given batch
    position = dm.importTrackingFile("position")
    sep_x = 0.9
    sep_y = 0.7
    
    # Telescope bin size in mm
    bin_size = 18.5 * 0.001
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    
    chans = peak_values.dtype.names

    # In case there are arrays in batch, produce seperately array plots
    produceArrayPlots(peak_values, np.copy(tracking), position, time_difference_peak, time_difference_rise_time_ref)


    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    channels = [x for x in chans if x != SiPM_chan]

    #channels = ["chan0"]

#    # Produce single pad plots
#    for chan in channels:
#
#            if not md.checkIfArrayPad(chan):
#
#                print "\nSingle pad", md.getNameOfSensor(chan), "\n"
#
#                pos_x = position[chan][0][0]
#                pos_y = position[chan][0][1]
#
#                tracking_chan = changeCenterPositionSensor(np.copy(tracking), pos_x, pos_y)
#
#                produceTProfilePlots(peak_values[chan], tracking_chan, time_difference_peak[chan], time_difference_rise_time_ref[chan], chan)
#                produceEfficiencyPlot(peak_values[chan], tracking_chan, chan)


###########################################
#                                         #
#  MEAN VALUE AND TIME RESOLUTION GRAPHS  #
#                                         #
###########################################


# Produce mean value and time resolution plots
def produceTProfilePlots(peak_values, tracking, time_difference_peak, time_difference_rise_time_ref, chan, array_pad=False):


    sep_x, sep_y, bin_size = getSepGlobVar()

    if array_pad:
        sep_x *= 1.9
        sep_y *= 1.9

    #bin_size *= 2.5

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

    # Fill mean values and time differences in each bin, for peak reference and rise time reference

    for event in range(0, len(tracking)):
        
        if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y) and peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
        
            mean_values[chan].Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])
            
            if time_difference_peak[event] != 0:

                timing_resolution_peak[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_peak[event])

            if time_difference_rise_time_ref[event] != 0:

                timing_resolution_rise_time_ref[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_rise_time_ref[event])


    sigma_sipm = 16.14

    # Filter bins and fill time resolution values
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = mean_values[chan].GetBin(i,j)
            num_mean = mean_values[chan].GetBinEntries(bin)
            num_time_peak = timing_resolution_peak[chan].GetBinEntries(bin)
            num_time_rtref = timing_resolution_rise_time_ref[chan].GetBinEntries(bin)
            
            if 0 < num_mean < minEntries:
                mean_values[chan].SetBinContent(bin, 0)
                mean_values[chan].SetBinEntries(bin, 0)

            if num_time_peak > minEntries:
                sigma_dut_conv = timing_resolution_peak[chan].GetBinError(bin)*1000

                if sigma_dut_conv > sigma_sipm:
                    sigma_dut = np.sqrt(sigma_dut_conv**2 - sigma_sipm**2)
                    timing_resolution_peak_copy[chan].SetBinContent(bin, sigma_dut)

            if num_time_rtref > minEntries:
                sigma_dut_conv_rt = timing_resolution_rise_time_ref[chan].GetBinError(bin)*1000
                
                if sigma_dut_conv_rt > sigma_sipm:
                    sigma_dut = np.sqrt(sigma_dut_conv_rt**2 - sigma_sipm**2)
                    timing_resolution_rise_time_ref_copy[chan].SetBinContent(bin, sigma_dut)


    mean_values[chan].ResetStats()
    ROOT.gStyle.SetOptStat(1)

    totalEntries = mean_values[chan].GetEntries()

    # Print mean value 2D plot
    headTitle = "Averaged pulse amplitude in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; V [mV]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/mean_value/tracking_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    mean_values[chan].SetAxisRange(-md.getPulseAmplitudeCut(chan)*1000, mean_values[chan].GetMaximum(), "Z")
    mean_values[chan].SetNdivisions(10, "Z")
    printTHPlot(mean_values[chan], titles)


    # Print time resolution peak reference
    headTitle = "Time resolution (peak ref) in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_peak_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    timing_resolution_peak_copy[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(timing_resolution_peak_copy[chan], titles)


    # Print time resolution rise time ref
    headTitle = "Time resolution (rise time ref) in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) +"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_rise_time_ref_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    timing_resolution_rise_time_ref_copy[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(timing_resolution_rise_time_ref_copy[chan], titles)


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking, chan, array_pad=False):

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
    LGAD[chan]         = ROOT.TH2F("LGAD_particles", "LGAD particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
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
        if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):
        
            # Total events
            MIMOSA[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)
            
            # Passed events
            if peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
                LGAD[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = MIMOSA[chan].GetBin(i,j)
            num_LGAD = LGAD[chan].GetBinContent(bin)
            
            if 0 < num_LGAD < minEntries:
                LGAD[chan].SetBinContent(bin, 0)
                MIMOSA[chan].SetBinContent(bin, 0)

    LGAD[chan].ResetStats()
    MIMOSA[chan].ResetStats()

    # Projection plot limits
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
                
                # The factor 4 is to compensate for 4 times the registered tracking info
                # The TEfficiency is scaled when the histogram is drawn
                if array_pad:
                    inefficiency[chan].SetBinContent(bin, 1-eff*4)
        
                else:
                    inefficiency[chan].SetBinContent(bin, 1-eff)


            elif eff == 1:
                inefficiency[chan].SetBinContent(bin, 0.001)
            

            # Get projection x data given limits
            if bin_low_x <= i <= bin_high_x:
                y_pos = LGAD[chan].GetYaxis().GetBinCenter(j)
                efficiency_projectionY[chan].Fill(y_pos, eff*100)
            
            # Get projection x data given limits
            if bin_low_y <= j <= bin_high_y:
                x_pos = LGAD[chan].GetXaxis().GetBinCenter(i)
                efficiency_projectionX[chan].Fill(x_pos, eff*100)


    # Create projection plots for single pad arrays only
    if not array_pad:
     
        fit_sigmoid_x = ROOT.TF1("sigmoid_x", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_x, sep_x)
        fit_sigmoid_x.SetParameters(100, 10, -0.5, 0.5)
        efficiency_projectionX[chan].Fit("sigmoid_x", "Q","", -sep_x, sep_x)
        
        fit_sigmoid_y = ROOT.TF1("sigmoid_y", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_y, sep_y)
        fit_sigmoid_y.SetParameters(100, 10, -0.5, 0.5)
        efficiency_projectionY[chan].Fit("sigmoid_y", "Q","", -sep_y, sep_y)
     
     
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
    
    
    totalEntries = efficiency[chan].GetPassedHistogram().GetEntries()

    # Print efficiency plot
    headTitle = "Efficiency in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; X [mm] ; Y [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName, totalEntries]
    printTHPlot(efficiency[chan], titles, True, False, array_pad)


    # Print inefficiency plot
    headTitle = "Inefficiency in each bin " + md.getNameOfSensor(chan) + " B" + str(md.getBatchNumber()) + "; X [mm] ; Y [mm] ; Inefficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName, totalEntries]
    inefficiency[chan].Scale(100)
    inefficiency[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(inefficiency[chan], titles, False, True, array_pad)



###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def produceArrayPlots(peak_values, tracking, position, time_difference_peak, time_difference_rise_time_ref):
    
    if md.getNameOfSensor("chan5") == "W4-S215" or md.getNameOfSensor("chan5") == "W4-S204_6e14":
        
        channels = ["chan5"]
        batchCategory = md.getBatchNumber()/100
        # W4-S204_6e14 -40 C
        if batchCategory == 5 or batchCategory == 7:
       
            # Calculate mean position from position of each array sensor
            array_pos_x = (position["chan6"][0][0] + position["chan7"][0][0])/2
            array_pos_y = (position["chan7"][0][1] + position["chan5"][0][1])/2
            
            changeCenterPositionSensor(tracking, array_pos_x, array_pos_y, True)

            # Concatenate max amplitude value info for each array sensor
            peak_values_array = np.concatenate((peak_values["chan5"], peak_values["chan6"], peak_values["chan7"]), axis=0)
            tracking_array = np.concatenate((tracking, tracking, tracking), axis=0)
            time_difference_peak_array = np.concatenate((time_difference_peak["chan5"], time_difference_peak["chan6"], time_difference_peak["chan7"]), axis=0)
            time_difference_rise_time_ref_array = np.concatenate((time_difference_rise_time_ref["chan5"], time_difference_rise_time_ref["chan6"], time_difference_rise_time_ref["chan7"]), axis=0)
        
        else:

            # W4-S215 22 C
            if int(md.getBatchNumber()/100) == 1:
            
                channels = ["chan4", "chan5", "chan6", "chan7"]


            # W4-S215 22 C
            elif int(md.getBatchNumber()/100) == 2:
                
                channels = ["chan3", "chan5", "chan6", "chan7"]
            


            # W4-S215 -30 C
            elif int(md.getBatchNumber()/100) == 4:
            
                channels = ["chan1", "chan5", "chan6", "chan7"]


            # Calculate mean position from position of each array sensor
            array_pos_x = (position[channels[0]][0][0] + position[channels[1]][0][0] + position[channels[2]][0][0] + position[channels[3]][0][0])/4
            array_pos_y = (position[channels[0]][0][1] + position[channels[1]][0][1] + position[channels[2]][0][1] + position[channels[3]][0][1])/4
            
            changeCenterPositionSensor(tracking, array_pos_x, array_pos_y, True)

            # Concatenate max amplitude value info for each array sensor
            peak_values_array = np.concatenate((peak_values[channels[0]], peak_values[channels[1]], peak_values[channels[2]], peak_values[channels[3]]), axis=0)
            tracking_array = np.concatenate((tracking, tracking, tracking, tracking), axis=0)
            time_difference_peak_array = np.concatenate((time_difference_peak[channels[0]], time_difference_peak[channels[1]], time_difference_peak[channels[2]], time_difference_peak[channels[3]]), axis=0)
            time_difference_rise_time_ref_array = np.concatenate((time_difference_rise_time_ref[channels[0]], time_difference_rise_time_ref[channels[1]], time_difference_rise_time_ref[channels[2]], time_difference_rise_time_ref[channels[3]]), axis=0)

        print "\nArray Pad", md.getNameOfSensor(channels[0]), "\n"

        produceTProfilePlots(peak_values_array, tracking_array, time_difference_peak_array, time_difference_rise_time_ref_array, channels[0], True)
        produceEfficiencyPlot(peak_values_array, tracking_array, channels[0], True)

        del channels

# Print TH2 Object plot
def printTHPlot(graphList, info, efficiency=False, inefficiency=False, array_pad=False):
    
    canvas.SetRightMargin(0.14)
    graphList.SetTitle(info[0])
    
    graphList.Draw("COLZ")
    canvas.Update()
    
    if efficiency:
    
        if array_pad:
            graphList.GetPaintedHistogram().Scale(4)

        # Get painted histogram by calling TEfficiency-object
        graphList.GetPaintedHistogram().Scale(100)
        graphList.GetPaintedHistogram().SetAxisRange(0, 100, "Z")
        graphList.GetPaintedHistogram().SetNdivisions(10, "Z")
        graphList.GetPaintedHistogram().SetTitle(info[0])
        
        # Update
        graphList.GetPaintedHistogram().Draw("COLZ")
        
        # Correct the number of entries, since PaintedHistogram have one per bin
        graphList.GetPaintedHistogram().SetStats(1)
        graphList.GetPaintedHistogram().SetEntries(info[2])
        
        ROOT.gStyle.SetOptStat(1000000011)
        
        # Move the stats box
        stats_box = graphList.GetPaintedHistogram().GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        
        # Recreate stats box
        stats_box.SetOptStat(1000000011)
        
        # Draw projection limit lines for x
        proj_line_selection_up = ROOT.TLine(-0.6, 0.3, 0.6, 0.3)
        proj_line_selection_down = ROOT.TLine(-0.6, -0.3, 0.6, -0.3)
        #proj_line_selection_up.Draw("same")
        #proj_line_selection_down.Draw("same")
        
    else:
        graphList.SetStats(1)
        graphList.SetEntries(info[2])
        ROOT.gStyle.SetOptStat(1000000011)
        
        # Move the stats box
        stats_box = graphList.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        
        # Recreate stats box
        stats_box.SetOptStat(1000000011)


    # Export PDF
    canvas.Print(info[1])
    
    # Export ROOT TH2 Histogram
    rootDestination = info[1].replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDestination = rootDestination.replace(".pdf", ".root")
    fileObject = ROOT.TFile(rootDestination, "RECREATE")
    fileObject.WriteTObject(graphList)
    fileObject.Close()

    canvas.Clear()



# Print projection plot
def printProjectionPlot(graphList, titles):

    ROOT.gStyle.SetOptStat(1)
    ROOT.gStyle.SetOptFit(1)

    graphList.SetTitle(titles[0])
    graphList.SetStats(1)
    graphList.Draw()
    canvas.Update()

    # Export PDF
    canvas.Print(titles[1])
    canvas.Clear()


# Change tracking information
def changeCenterPositionSensor(tracking, pos_x, pos_y, array_pad=False):

    tracking["X"] = np.multiply(tracking["X"], 0.001) - pos_x
    tracking["Y"] = np.multiply(tracking["Y"], 0.001) - pos_y

    if array_pad:
        
        # Rotation for W4-S204_6e14
        tan_theta = 0.15/1.75

        if md.getNameOfSensor("chan5") == "W4-S215":
        
            tan_theta = 4./300
    
        cos_theta = np.sqrt(1./(1+np.power(tan_theta, 2)))
        sin_theta = np.sqrt(1-np.power(cos_theta, 2))

        tracking["X"] = np.multiply(tracking["X"], cos_theta) - np.multiply(tracking["Y"], sin_theta)
        tracking["Y"] = np.multiply(tracking["X"], sin_theta) + np.multiply(tracking["Y"], cos_theta)


    return tracking


# Time diff in ns
def getSigmaPerBin(time_difference, tracking, x_pos, y_pos, bin_size, chan):

    selection_x  = (tracking["X"] < x_pos + bin_size/2) & (tracking["X"] > x_pos - bin_size/2)
    selection_y  = (tracking["Y"] < y_pos + bin_size/2) & (tracking["Y"] > y_pos - bin_size/2)
    
    time_diff_bin = time_difference[(selection_x & selection_y)]
    
    time_diff_bin = np.multiply(time_diff_bin, 1000)
    
    mean_value_time_diff = np.average(time_diff_bin)
    N = 3
    xMin = np.average(time_diff_bin) - N * np.std(time_diff_bin)
    xMax = np.average(time_diff_bin) + N * np.std(time_diff_bin)

    hist = ROOT.TH1D("Time difference bin", "time_diff_bin", 10, xMin, xMax)

    
    for entry in range(0, len(time_diff_bin)):
        hist.Fill(time_diff_bin[entry])


    fit_function, sigma_DUT = t_calc.getFitFunction(hist, chan)

    del hist

    return sigma_DUT



# Return global varables, separation and bin size
def getSepGlobVar():

    return sep_x, sep_y, bin_size
