import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import tracking_calc as t_calc

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(20)

def produceTrackingGraphs(peak_values, rise_times, tracking, time_difference_peak, time_difference_cfd05):
   
    global canvas
    global bin_size
    global minEntries
    global fill_range
    
    t_calc.setArrayPadExportBool(False)
    
    # Convert pulse amplitude values from [-V] to [+mV], rise time from [ns] to [ps] and position from [um] to [mm]
    position = dm.importTrackingFile("position")
    position = dm.convertPositionData(position)
    peak_values = dm.convertPulseData(peak_values)
    rise_times = dm.convertRiseTimeData(rise_times)
    
    canvas = ROOT.TCanvas("Tracking", "tracking")

    # Bin size resolution of the MIMOSA
    fill_range = [0.85, 0.65]
    bin_size = 18.5 * 0.001 * 2
    minEntries = 5
    
    if md.getNumberOfRunsPerBatch() > 2 and md.getBatchNumber() != 203:
        bin_size *= 0.5
        minEntries = 10


#    createSinglePadGraphs(peak_values, rise_times, time_difference_peak, time_difference_cfd05, tracking, position)

    createArrayPadGraphs(position)


###########################################
#                                         #
#           SINGLE PAD GRAPHS             #
#                                         #
###########################################



def createSinglePadGraphs(peak_values, rise_times, time_difference_peak, time_difference_cfd05, tracking, position):
    
    global chan

    # Produce single pad plots
    for chan in peak_values.dtype.names:
    
        if md.getNameOfSensor(chan) == "SiPM-AFP":
            continue

        print "\nSingle pad", md.getNameOfSensor(chan), "\n"

        tracking_chan = t_calc.changeCenterPositionSensor(np.copy(tracking), position, chan)

        produceTProfilePlots(peak_values[chan], rise_times[chan], tracking_chan, time_difference_peak[chan], time_difference_cfd05[chan])
        produceEfficiencyPlot(peak_values[chan], tracking_chan)



###########################################
#                                         #
#       ARRAY PAD GRAPHS (not done)       #
#                                         #
###########################################


def createArrayPadGraphs(position):
    
    global chan
    t_calc.setArrayPadExportBool(True)
    
    [sep_x, sep_y] = getFillRange()
 
    sep_x *= 2
    sep_y *= 2
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    # The binning for the timing resolution are decreased
    bin_timing_decrease = 1.8
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)
    
    arrayPadChannels = t_calc.getArrayPadChannels()
    chan = arrayPadChannels[0]

    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_cfd05_th2d = ROOT.TH2D("Timing resolution cfd05", "timing resolution cfd05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    efficiency_th2d = ROOT.TH2D("Efficiency", "Efficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    inefficiency_th2d = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    TH2D_objects_list = [peak_value_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd05_th2d, efficiency_th2d, inefficiency_th2d]

    print "\nArray Pad", md.getNameOfSensor(chan), "\n"
    
    for TH2D_object in TH2D_objects_list:
        for index in range(0, len(arrayPadChannels)):
            
            t_calc.importAndAddHistogram(TH2D_object, index)


    # Print pulse amplitude mean value 2D plot
    peak_value_mean_th2d.SetAxisRange(0, peak_value_mean_th2d.GetMaximum(), "Z")
    peak_value_mean_th2d.SetNdivisions(10, "Z")
    printTHPlot(peak_value_mean_th2d)
    
    # Print rise time mean value 2D plot
    peak_value_mean_th2d.SetAxisRange(rise_time_mean_th2d.GetMaximum()-400, rise_time_mean_th2d.GetMaximum()+400, "Z")
    peak_value_mean_th2d.SetNdivisions(10, "Z")
    printTHPlot(rise_time_mean_th2d)


    # Print time resolution peak reference
    timing_peak_th2d.SetAxisRange(0, 200, "Z")
    printTHPlot(timing_peak_th2d)

    # Print time resolution cfd05 ref
    timing_cfd05_th2d.SetAxisRange(0, 200, "Z")
    printTHPlot(timing_cfd05_th2d)

    efficiency_th2d.SetAxisRange(0, 100, "Z")
    printTHPlot(efficiency_th2d)

    inefficiency_th2d.SetAxisRange(0, 100, "Z")
    printTHPlot(inefficiency_th2d)



###########################################
#                                         #
#  MEAN VALUE AND TIME RESOLUTION GRAPHS  #
#                                         #
###########################################


# Produce mean value and time resolution plots
def produceTProfilePlots(peak_values, rise_times, tracking, time_difference_peak, time_difference_cfd05):

    [sep_x, sep_y] = getFillRange()

    if md.checkIfArrayPad(chan):
    
        sep_x *= 2
        sep_y *= 2
    
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)

    # The binning for the timing resolution are decreased
    bin_timing_decrease = 1.8
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)
    
    # Constraints for filling time difference values
    window = 1000
    mpv_time_diff_peak =  np.average(time_difference_peak[np.nonzero(time_difference_peak)])
    mpv_time_diff_cfd05 =  np.average(time_difference_cfd05[np.nonzero(time_difference_cfd05)])

    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)

    timing_peak_th2d_temp = ROOT.TProfile2D("Timing resolution peak temp", "timing resolution peak temp", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    timing_cfd05_th2d_temp = ROOT.TProfile2D("Timing resolution cfd05 temp", "timing resolution cfd05 temp", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")

    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_cfd05_th2d = ROOT.TH2D("Timing resolution cfd05", "timing resolution cfd05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)

    # Fill mean values and time differences in each bin, for peak reference and rise time reference
    for event in range(0, len(tracking)):

        if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):

            if peak_values[event] != 0:
            
                peak_value_mean_th2d.Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])
            
            if rise_times[event] != 0:
            
                rise_time_mean_th2d.Fill(tracking['X'][event], tracking['Y'][event], rise_times[event])
        
            # Introduce additional constraint to take away extreme values which causes the error to be large
            if time_difference_peak[event] != 0 and (mpv_time_diff_peak - window < time_difference_peak[event] < mpv_time_diff_peak + window):

                timing_peak_th2d_temp.Fill(tracking['X'][event], tracking['Y'][event], time_difference_peak[event])
            
            # Introduce additional constraint to take away extreme values which causes the error to be large
            if time_difference_cfd05[event] != 0 and (mpv_time_diff_cfd05 - window < time_difference_cfd05[event] < mpv_time_diff_cfd05 + window):

                timing_cfd05_th2d_temp.Fill(tracking['X'][event], tracking['Y'][event], time_difference_cfd05[event])


    # Get width of the SiPM
    sigma_SiPM = md.getSigmaSiPM()
    
    # Filter pulse amplitude and rise time mean value bins
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = peak_value_mean_th2d.GetBin(i,j)
            num_mean = peak_value_mean_th2d.GetBinEntries(bin)
            num_rise = rise_time_mean_th2d.GetBinEntries(bin)
            
            if num_mean < minEntries:
                peak_value_mean_th2d.SetBinContent(bin, 0)
                peak_value_mean_th2d.SetBinEntries(bin, 0)
            
            if num_rise < minEntries:
                rise_time_mean_th2d.SetBinContent(bin, 0)
                rise_time_mean_th2d.SetBinEntries(bin, 0)
            

    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
        
            bin = timing_peak_th2d_temp.GetBin(i,j)
            num_time_peak = timing_peak_th2d_temp.GetBinEntries(bin)
            num_time_cfd = timing_cfd05_th2d_temp.GetBinEntries(bin)
            
            if num_time_peak > 10:

                sigma_convoluted_peak = timing_peak_th2d_temp.GetBinError(bin)
                sigma_DUT = np.sqrt(np.power(sigma_convoluted_peak, 2) - np.power(sigma_SiPM, 2))
                timing_peak_th2d.SetBinContent(bin, sigma_DUT)

            if num_time_cfd > 10:

                sigma_convoluted_cfd05 = timing_cfd05_th2d_temp.GetBinError(bin)
                sigma_DUT = np.sqrt(np.power(sigma_convoluted_cfd05, 2) - np.power(sigma_SiPM, 2))
                timing_cfd05_th2d.SetBinContent(bin, sigma_DUT)


    peak_value_mean_th2d.ResetStats()
    rise_time_mean_th2d.ResetStats()
    timing_peak_th2d_temp.ResetStats()
    timing_cfd05_th2d_temp.ResetStats()
    ROOT.gStyle.SetOptStat(1)


    # Print pulse amplitude mean value 2D plot
    peak_value_mean_th2d.SetAxisRange(0, peak_value_mean_th2d.GetMaximum(), "Z")
    peak_value_mean_th2d.SetNdivisions(10, "Z")
    printTHPlot(peak_value_mean_th2d)


    # Print rise time mean value 2D plot
    rise_time_mean_th2d.SetAxisRange(rise_time_mean_th2d.GetMaximum()-400, rise_time_mean_th2d.GetMaximum()+400, "Z")
    rise_time_mean_th2d.SetNdivisions(10, "Z")
    printTHPlot(rise_time_mean_th2d)


    # Print time resolution peak reference
    totalEntries = timing_peak_th2d_temp.GetEntries()
    timing_peak_th2d.SetAxisRange(0, 200, "Z")
    printTHPlot(timing_peak_th2d, totalEntries)


    # Print time resolution cfd05 ref
    totalEntries = timing_cfd05_th2d_temp.GetEntries()
    timing_cfd05_th2d.SetAxisRange(0, 200, "Z")
    printTHPlot(timing_cfd05_th2d, totalEntries)


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking):

    [sep_x, sep_y] = getFillRange()
    
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

    # Projection plot limits
    bin_low_x = LGAD_th2d.GetXaxis().FindBin(-0.3)
    bin_high_x = LGAD_th2d.GetXaxis().FindBin(0.3)

    bin_low_y = LGAD_th2d.GetYaxis().FindBin(-0.3)
    bin_high_y = LGAD_th2d.GetYaxis().FindBin(0.3)

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
            if bin_low_x <= i <= bin_high_x:
                y_pos = LGAD_th2d.GetYaxis().GetBinCenter(j)
                projectionY_th1d.Fill(y_pos, eff)
            
            # Get projection y data given limits
            if bin_low_y <= j <= bin_high_y:
                x_pos = LGAD_th2d.GetXaxis().GetBinCenter(i)
                projectionX_th1d.Fill(x_pos, eff)


    # Create projection plots for single pad arrays only
    produceProjectionPlots(projectionX_th1d, projectionY_th1d, sep_x, sep_y)
    
    
    totalEntries = efficiency_TEff.GetPassedHistogram().GetEntries()

    efficiency_TEff.Draw("COLZ")
    canvas.Update()
    efficiency_TH2D = efficiency_TEff.GetPaintedHistogram()
    efficiency_TH2D.Scale(100)
    efficiency_TH2D.SetAxisRange(0, 100, "Z")
    efficiency_TH2D.SetName("Efficiency")
    printTHPlot(efficiency_TH2D, totalEntries)

    inefficiency_th2d.SetAxisRange(0, 100, "Z")
    printTHPlot(inefficiency_th2d, totalEntries)



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
    canvas.Update()
    
    # Export PDF and Histogram
    canvas.Print(fileName)
    dm.exportROOTHistogram(graphList, fileName)
    canvas.Clear()


def produceProjectionPlots(projectionX_th1d, projectionY_th1d, sep_x, sep_y):

    fit_sigmoid_x = ROOT.TF1("sigmoid_x", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_x, sep_x)
    fit_sigmoid_x.SetParameters(100, 70, -0.5, 0.5)
    fit_sigmoid_x.SetParNames("Constant", "k", "Pos left", "Pos right")
    projectionX_th1d.Fit("sigmoid_x", "Q","", -sep_x, sep_x)
    
    fit_sigmoid_y = ROOT.TF1("sigmoid_y", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_y, sep_y)
    fit_sigmoid_y.SetParameters(100, 70, -0.5, 0.5)
    fit_sigmoid_x.SetParNames("Constant", "k", "Pos left", "Pos right")
    projectionY_th1d.Fit("sigmoid_y", "Q","", -sep_y, sep_y)
 
 
    # Print projection X plot
    headTitle = "Projection of X-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printProjectionPlot(projectionX_th1d, titles)
    
    # Print projection Y plot
    headTitle = "Projection of Y-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; Y [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionY_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    titles = [headTitle, fileName]
    printProjectionPlot(projectionY_th1d, titles)


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


def getFillRange():

    return fill_range[0], fill_range[1]

