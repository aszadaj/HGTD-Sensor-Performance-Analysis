import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_calculations as t_calc

n_div = 10 # Number of ticks on Z-axis

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(n_div)

def produceTrackingGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd05, tracking):
   
    global canvas
    global glob_variables
    
    
    # Bin size resolution of the MIMOSA and to fill seen from the center of the pad (in um)
    sep_x = 850 # Width from the center of the canvas in x
    sep_y = 650 # Width from the center of the canvas in y
    entries_per_bin = 50 # Required entries for timing resolution graphs
    bin_size = 18.5 # Pixel size from the MIMOSA/tracking
    minEntries = 5 # Minimum entries per bin
    bin_timing_decrease = 3 # Increment of the bin size for the timing resolution
    width_time_diff = 300 # Width from the mean value of filling time difference values
    peak_value_max = 300 # Z-axis limit for mean pulse amplitude graph
    rise_time_max = 1550 # Z-axis limit for rise time graph
    timing_res_max = 100 # Z-axis limit for timing resolution graph
    gain_max = 100 # Z-axis limit for mean gain graph
    max_factor_filling = 20 # Increment of the limits to fill in the TH2/TProfile2D objects
    
    glob_variables = [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff]
    
    t_calc.setArrayPadExportBool(False)
    
    # Convert pulse amplitude values from [-V] to [+mV], charge from [C] to [fC] to gain, rise time from [ns] to [ps]
    dm.convertPulseData(peak_values)
    dm.convertChargeToGainData(gain)
    dm.convertRiseTimeData(rise_times)
    
    canvas = ROOT.TCanvas("Tracking", "tracking")

    createSinglePadGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd05, tracking)

    # Create array pad graphs for all batches, except batch 80X
    if md.getBatchNumber()/100 != 8 and md.sensor == "":
        createArrayPadGraphs()


###########################################
#                                         #
#           SINGLE PAD GRAPHS             #
#                                         #
###########################################



def createSinglePadGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd05, tracking):
    
    global chan
    global singlePadGraphs
    singlePadGraphs = True
    
    # Produce single pad plots
    for chan in peak_values.dtype.names:

        if md.getNameOfSensor(chan) == "SiPM-AFP":
            continue
        
        if md.getNameOfSensor(chan) != md.sensor and md.sensor != "":
            continue
    
        print "\nSingle pad", md.getNameOfSensor(chan), "\n"

        tracking_chan = t_calc.changeCenterPositionSensor(np.copy(tracking))

        produceTProfilePlots(peak_values[chan], gain[chan], rise_times[chan], tracking_chan, time_difference_peak[chan], time_difference_cfd05[chan])
        produceEfficiencyPlot(peak_values[chan], tracking_chan)



#########################################################
#                                                       #
#   GAIN, PULSE MEAN VALUE AND TIME RESOLUTION GRAPHS   #
#                                                       #
#########################################################


# Produce mean value and time resolution plots
def produceTProfilePlots(peak_values, gain, rise_times, tracking, time_difference_peak, time_difference_cfd05):
    
    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff] = [i for i in glob_variables]

    
    # Specially for W4-RD01, increase the limit to include large gain values
    if md.getNameOfSensor(chan) == "W4-RD01":
        gain_max *= 5

    if md.checkIfArrayPad(chan):
    
        sep_x *= 2
        sep_y *= 2
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    mpv_time_diff_peak  =  np.average(time_difference_peak[np.nonzero(time_difference_peak)])
    mpv_time_diff_cfd05 =  np.average(time_difference_cfd05[np.nonzero(time_difference_cfd05)])

    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    gain_mean_th2d = ROOT.TProfile2D("Gain mean value","Gain mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    
    time_difference_peak_th2d = ROOT.TProfile2D("Time difference peak", "Time difference peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    time_difference_cfd05_th2d = ROOT.TProfile2D("Time difference cfd05", "Time difference cfd05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_cfd05_th2d = ROOT.TH2D("Timing resolution cfd05", "timing resolution cfd05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    
    # Fill mean values and time differences in each bin, for peak reference and rise time reference
    for event in range(0, len(tracking)):

        if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):

            if 0 < peak_values[event] < peak_value_max * max_factor_filling:
            
                peak_value_mean_th2d.Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])
            
            if 0 < gain[event] < gain_max * max_factor_filling:
            
                gain_mean_th2d.Fill(tracking['X'][event], tracking['Y'][event], gain[event])
            
            if 0 < rise_times[event] < rise_time_max * max_factor_filling:
            
                rise_time_mean_th2d.Fill(tracking['X'][event], tracking['Y'][event], rise_times[event])
        
            # Introduce additional constraint to take away extreme values which causes the error to be large
            if time_difference_peak[event] != 0 and (mpv_time_diff_peak - width_time_diff < time_difference_peak[event] < mpv_time_diff_peak + width_time_diff):

                time_difference_peak_th2d.Fill(tracking['X'][event], tracking['Y'][event], time_difference_peak[event])
            
            # Introduce additional constraint to take away extreme values which causes the error to be large
            if time_difference_cfd05[event] != 0 and (mpv_time_diff_cfd05 - width_time_diff < time_difference_cfd05[event] < mpv_time_diff_cfd05 + width_time_diff):

                time_difference_cfd05_th2d.Fill(tracking['X'][event], tracking['Y'][event], time_difference_cfd05[event])

    # Filter pulse amplitude and rise time mean value bins
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = peak_value_mean_th2d.GetBin(i,j)
            t_calc.removeBin(bin, peak_value_mean_th2d, minEntries)
            t_calc.removeBin(bin, rise_time_mean_th2d, minEntries)
            t_calc.removeBin(bin, gain_mean_th2d, minEntries)

    peak_value_mean_th2d.ResetStats()
    rise_time_mean_th2d.ResetStats()
    gain_mean_th2d.ResetStats()

    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
        
            bin = time_difference_peak_th2d.GetBin(i,j)
            t_calc.fillTimeResBin(bin, time_difference_peak_th2d, timing_peak_th2d)
            t_calc.fillTimeResBin(bin, time_difference_cfd05_th2d, timing_cfd05_th2d)

    ROOT.gStyle.SetOptStat(1)


    # Print pulse amplitude mean value 2D plot
    peak_value_mean_th2d.SetAxisRange(0, peak_value_max, "Z")
    peak_value_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(peak_value_mean_th2d)

    # Print gain mean value 2D plot
    gain_mean_th2d.SetAxisRange(0, gain_max, "Z")
    gain_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(gain_mean_th2d)


    # Print rise time mean value 2D plot
    rise_time_mean_th2d.SetAxisRange(0, rise_time_max, "Z")
    rise_time_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(rise_time_mean_th2d)


    # Print time resolution peak reference
    totalEntries = time_difference_peak_th2d.GetEntries()
    timing_peak_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_peak_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_peak_th2d, totalEntries)


    # Print time resolution cfd05 ref
    totalEntries = time_difference_cfd05_th2d.GetEntries()
    timing_cfd05_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_cfd05_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_cfd05_th2d, totalEntries)


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking):

    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff] = [i for i in glob_variables]
    
    if md.checkIfArrayPad(chan):
    
        sep_x *= 2
        sep_y *= 2

    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)

    # Fill events for which the sensors records a hit
    LGAD_th2d         = ROOT.TH2D("LGAD_particles", "LGAD particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA_th2d       = ROOT.TH2D("tracking_particles", "Tracking particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # For a given TEfficiency object, recreate to make it an inefficiency
    inefficiency_th2d = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Projection X of efficiency
    projectionX_th1d = ROOT.TProfile("Projection X", "projection x", xbin, -sep_x,sep_x)
    
    # Projection Y of efficiency
    projectionY_th1d = ROOT.TProfile("Projection Y", "projection y", ybin, -sep_y,sep_y)
    
    
    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):
    
            # Total events
            MIMOSA_th2d.Fill(tracking['X'][event], tracking['Y'][event], 1)
            
            # Passed events
            if peak_values[event] != 0:
                LGAD_th2d.Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = LGAD_th2d.GetBin(i,j)
            num_LGAD = LGAD_th2d.GetBinContent(bin)
            
            if num_LGAD < minEntries:
                LGAD_th2d.SetBinContent(bin, 0)
                MIMOSA_th2d.SetBinContent(bin, 0)


    LGAD_th2d.ResetStats()
    MIMOSA_th2d.ResetStats()


    distance_projection, center_positions = t_calc.findSelectionRange()

    # Projection plot limits
    bin_x = np.array([LGAD_th2d.GetXaxis().FindBin(distance_projection[0][0]), LGAD_th2d.GetXaxis().FindBin(distance_projection[0][1])])
    bin_y = np.array([LGAD_th2d.GetYaxis().FindBin(distance_projection[1][0]), LGAD_th2d.GetYaxis().FindBin(distance_projection[1][1])])
    

    # Efficiency object
    efficiency_TEff = ROOT.TEfficiency(LGAD_th2d, MIMOSA_th2d)

    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = efficiency_TEff.GetGlobalBin(i,j)
            eff = efficiency_TEff.GetEfficiency(bin)*100

            if eff > 0:
                inefficiency_th2d.SetBinContent(bin, 100-eff)
            
            if eff == 100:
                inefficiency_th2d.SetBinContent(bin, 0.001)
    
            # Get projection x data given limits
            if bin_x[0] <= i <= bin_x[1]:
                y = LGAD_th2d.GetYaxis().GetBinCenter(j)
                projectionY_th1d.Fill(y, eff)
            
            # Get projection y data given limits
            if bin_y[0] <= j <= bin_y[1]:
                x = LGAD_th2d.GetXaxis().GetBinCenter(i)
                projectionX_th1d.Fill(x, eff)

    # Create projection plots for single pad arrays only
    produceProjectionPlots(projectionX_th1d, projectionY_th1d, center_positions)

    del projectionX_th1d, projectionY_th1d, LGAD_th2d, MIMOSA_th2d
    
    totalEntries = efficiency_TEff.GetPassedHistogram().GetEntries()

    efficiency_TEff.Draw("COLZ")
    canvas.Update()
    efficiency_TH2D = efficiency_TEff.GetPaintedHistogram()
    efficiency_TH2D.Scale(100)
    efficiency_TH2D.SetAxisRange(0, 100, "Z")
    efficiency_TH2D.SetName("Efficiency")
    printTHPlot(efficiency_TH2D, totalEntries)

    del efficiency_TEff, efficiency_TH2D

    inefficiency_th2d.SetAxisRange(0, 100, "Z")
    printTHPlot(inefficiency_th2d, totalEntries)



###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def createArrayPadGraphs():

    global chan
    global singlePadGraphs
    singlePadGraphs = False
    
    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff] = [i for i in glob_variables]
 
    sep_x *= 2
    sep_y *= 2
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    # The binning for the timing resolution are decreased
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    arrayPadChannels = t_calc.getArrayPadChannels()
    chan = arrayPadChannels[0]
    
    # Specially for W4-RD01, increase the limit to include large gain values
    if md.getNameOfSensor(chan) == "W4-RD01":
        gain_max *= 5

    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    gain_mean_th2d = ROOT.TProfile2D("Gain mean value","Gain mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    
    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_cfd05_th2d = ROOT.TH2D("Timing resolution cfd05", "timing resolution cfd05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    
    efficiency_th2d = ROOT.TH2D("Efficiency", "Efficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    inefficiency_th2d = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    TH2D_objects_list = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd05_th2d, efficiency_th2d, inefficiency_th2d]

    print "\nArray Pad", md.getNameOfSensor(chan), "\n"
    
    for TH2D_object in TH2D_objects_list:
        for index in range(0, len(arrayPadChannels)):
         
            t_calc.importAndAddHistogram(TH2D_object, index)


    # Change the file names of the exported files (array)
    t_calc.setArrayPadExportBool(True)

    # Print pulse amplitude mean value 2D plot
    peak_value_mean_th2d.SetAxisRange(0, peak_value_max, "Z")
    peak_value_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(peak_value_mean_th2d)
    
    # Print pulse amplitude mean value 2D plot
    gain_mean_th2d.SetAxisRange(0, gain_max, "Z")
    gain_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(gain_mean_th2d)
    
    # Print rise time mean value 2D plot
    rise_time_mean_th2d.SetAxisRange(0, rise_time_max, "Z")
    rise_time_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(rise_time_mean_th2d)

    # Print time resolution peak reference
    timing_peak_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_peak_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_peak_th2d)

    # Print time resolution cfd05 ref
    timing_cfd05_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_cfd05_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_cfd05_th2d)
    
    
    
    # Print efficiency plot
    low_percent = 0
    efficiency_th2d.SetAxisRange(low_percent, 100, "Z")
    printTHPlot(efficiency_th2d)

    # Print inefficiency plots
    inefficiency_th2d.SetAxisRange(low_percent, 100, "Z")
    printTHPlot(inefficiency_th2d)



###########################################
#                                         #
#          PROJECTION FUNCTIONS           #
#                                         #
###########################################



def produceProjectionPlots(projectionX_th1d, projectionY_th1d, center_positions):

    # Distance from the center for selecting where the fit should be applied
    separation_distance = 600
    approx_width_projection = 10
    
    x_ranges = [center_positions[0] - separation_distance, center_positions[0] + separation_distance]
    y_ranges = [center_positions[1] - separation_distance, center_positions[1] + separation_distance]
    
    fit_sigmoid_x = ROOT.TF1("sigmoid_x", "[0]*(1/(1+TMath::Exp(([1]-x)/[3]))-1/(1+TMath::Exp(([2]-x)/[3])))", x_ranges[0], x_ranges[1])
    fit_sigmoid_x.SetParameters(100, x_ranges[0], x_ranges[1], approx_width_projection)
    fit_sigmoid_x.SetParNames("Constant", "Left", "Right", "\sigma = ")
    projectionX_th1d.Fit("sigmoid_x", "QR")


    fit_sigmoid_y = ROOT.TF1("sigmoid_y", "[0]*(1/(1+TMath::Exp(([1]-x)/[3]))-1/(1+TMath::Exp(([2]-x)/[3])))", y_ranges[0], y_ranges[1])
    fit_sigmoid_y.SetParameters(100, y_ranges[0], y_ranges[1], approx_width_projection)
    fit_sigmoid_y.SetParNames("Constant", "Left", "Right", "\sigma = ")
    projectionY_th1d.Fit("sigmoid_y", "QR")

    # Print projection X plot
    headTitle = "Projection of X-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+ "; X [\mum] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    
    printProjectionPlot(projectionX_th1d, titles)
    
    # Print projection Y plot
    headTitle = "Projection of Y-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+ "; Y [\mum] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionY_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printProjectionPlot(projectionY_th1d, titles)



###########################################
#                                         #
#        PRINT FUNCTIONS GRAPHS           #
#                                         #
###########################################


# Print TH2 Object plot
def printTHPlot(graphList, entries=0):
    
    if entries == 0:
        entries = graphList.GetEntries()
    
    objectName = graphList.GetName()
    fileName, headTitle = t_calc.getTitleAndFileName(objectName, chan)

    graphList.SetTitle(headTitle)
    canvas.SetRightMargin(0.14)
    graphList.SetStats(1)
    graphList.Draw("COLZ")
    canvas.Update()

    # Move the stats box
    stats_box = graphList.GetListOfFunctions().FindObject("stats")
    stats_box.SetX1NDC(0.1)
    stats_box.SetX2NDC(0.3)
    stats_box.SetY1NDC(0.93)
    stats_box.SetY2NDC(0.83)

    # Recreate stats box
    stats_box.SetOptStat(1000000011)
    graphList.SetEntries(entries)
    
    # Draw again to update the canvas
    graphList.Draw("COLZ")

    t_calc.drawLines()

    canvas.Update()
    
    # Export PDF and Histogram
    canvas.Print(fileName)
    dm.exportROOTHistogram(graphList, fileName)
    canvas.Clear()


# Print projection plot
def printProjectionPlot(graphList, info):


    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)
    ROOT.gStyle.SetStatW(0.15)


    graphList.SetTitle(info[0])
    graphList.SetStats(1)
    graphList.Draw()
    canvas.Update()
    

    # Export PDF
    canvas.Print(info[1])
    
    # Export histogram as ROOT file
    dm.exportROOTHistogram(graphList, info[1])
    canvas.Clear()
