import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_calculations as t_calc

n_div = 10 # Number of ticks on Z-axis

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(2*n_div)

def produceTrackingGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking):
   
    global canvas, canvas_projection
    global glob_variables
    
    
    sep_x = 800 # Width from the center of the canvas in x
    sep_y = 600 # Width from the center of the canvas in y
    entries_per_bin = 50 # Required entries for timing resolution graphs
    bin_size = 18.5 # Pixel size from the MIMOSA
    minEntries = 5 # Minimum entries per bin
    bin_timing_decrease = 3 # Increment of the bin size for the timing resolution
    width_time_diff = 300 # Width from the mean value of filling time difference values
    peak_value_max = 300 # Z-axis limit for mean pulse amplitude graph
    rise_time_max = 300 # Z-axis limit for rise time graph
    timing_res_max = 100 # Z-axis limit for timing resolution graph
    gain_max = 100 # Z-axis limit for mean gain graph
    max_factor_filling = 20 # Increment of the limits to fill in the TH2/TProfile2D objects
    percentage_efficiency = 80 # Limit the lower percentage
    
    glob_variables = [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff, percentage_efficiency]
    
    t_calc.setArrayPadExportBool(False)
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    canvas_projection = ROOT.TCanvas("Projection", "projection")
    
    # Convert pulse amplitude values from [-V] to [+mV], charge from [C] to [fC] to gain, rise time from [ns] to [ps]
    dm.changeIndexNumpyArray(peak_values, -1000)
    
    # Conversion of charge to gain, following a charge from a MIP, which is for a pion
    # 0.46 fC -> Gain = charge/MIP and convert to fC
    dm.changeIndexNumpyArray(gain, 1./(0.46*10**-15))
    dm.changeIndexNumpyArray(rise_times, 1000)

    createSinglePadGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking)

    # Create array pad graphs for all batches, except batch 80X
    if t_calc.sensorIsAnArrayPad():
        createArrayPadGraphs()


###########################################
#                                         #
#           SINGLE PAD GRAPHS             #
#                                         #
###########################################



def createSinglePadGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking):
    
    global chan
    global singlePadGraphs
    singlePadGraphs = True
    
    # Produce single pad plots
    for chan in peak_values.dtype.names:
        
        if (md.getNameOfSensor(chan) != md.sensor and md.sensor != "") or md.getNameOfSensor(chan) == "SiPM-AFP":
            continue
    
        print "\nSingle pad", md.getNameOfSensor(chan), "\n"

        # This function requires a ROOT file which have the center positions for each pad
        tracking_chan = t_calc.changeCenterPositionSensor(np.copy(tracking))

        produceTProfilePlots(peak_values[chan], gain[chan], rise_times[chan], tracking_chan, time_difference_peak[chan], time_difference_cfd[chan])
        produceEfficiencyPlot(peak_values[chan], tracking_chan)



#########################################################
#                                                       #
#   GAIN, PULSE MEAN VALUE AND TIME RESOLUTION GRAPHS   #
#                                                       #
#########################################################


# Produce mean value and time resolution plots
def produceTProfilePlots(peak_values, gain, rise_times, tracking, time_difference_peak, time_difference_cfd):
    
    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff, percentage_efficiency] = [i for i in glob_variables]

    
    # Specially for W4-RD01, increase the limit to include large gain values
    if md.getNameOfSensor(chan) == "W4-RD01":
        gain_max *= 5


    if md.checkIfArrayPad(chan):
    
        sep_x *= 2
        sep_y *= 2
    
    # Adaptive bin number
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    # Decreased number of bins for timing resolution plots
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    # Import values mean values of the time difference
    mpv_time_diff_peak =  dm.exportImportROOTData("results", "timing_normal", False,0, chan, md.checkIfSameOscAsSiPM(chan))["timing_normal"][2]
    mpv_time_diff_cfd  =  dm.exportImportROOTData("results", "timing_normal", False,0, chan, md.checkIfSameOscAsSiPM(chan), True)["timing_normal_cfd"][2]

    # Declare ROOT objects
    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    gain_mean_th2d = ROOT.TProfile2D("Gain mean value","Gain mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)
    
    time_difference_peak_th2d = ROOT.TProfile2D("Time difference peak", "Time difference peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    time_difference_cfd_th2d = ROOT.TProfile2D("Time difference cfd", "Time difference cfd", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_cfd_th2d = ROOT.TH2D("Timing resolution cfd", "timing resolution cfd", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    
    
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
            if time_difference_cfd[event] != 0 and (mpv_time_diff_cfd - width_time_diff < time_difference_cfd[event] < mpv_time_diff_cfd + width_time_diff):

                time_difference_cfd_th2d.Fill(tracking['X'][event], tracking['Y'][event], time_difference_cfd[event])

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
            t_calc.fillTimeResBin(bin, time_difference_cfd_th2d, timing_cfd_th2d)


    # Print pulse amplitude mean value 2D plot
    TH2D_objects = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd_th2d, 0, 0]
    limits = [peak_value_max, rise_time_max, timing_res_max, gain_max, time_difference_peak_th2d.GetEntries(), time_difference_cfd_th2d.GetEntries(), percentage_efficiency]
    setPlotLimitsAndPrint(TH2D_objects, limits)

    del peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, time_difference_peak_th2d, time_difference_cfd_th2d, timing_peak_th2d, timing_cfd_th2d


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking):

    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max,
    timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff, percentage_efficiency] = [i for i in glob_variables]
    
    if md.checkIfArrayPad(chan):
    
        sep_x *= 2
        sep_y *= 2

    # Define how many bins to use for the TH2-objects
    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)

    # Fill events for which the sensors records a hit
    LGAD_th2d         = ROOT.TH2D("LGAD_particles", "LGAD particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA_th2d       = ROOT.TH2D("tracking_particles", "Tracking particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    
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
    
    # Create efficiency and inefficiency objects
    efficiency_TEff = ROOT.TEfficiency(LGAD_th2d, MIMOSA_th2d)
    inefficiency_TH2D = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)

    # Total entries refer to pass events, that is number of recorded pixels on the sensor given a hit
    # in the MIMOSA. This number is used for both efficiency and inefficiency plots.
    totalEntries = efficiency_TEff.GetPassedHistogram().GetEntries()

    # Draw the TEfficiency object, and rescale it
    efficiency_TEff.Draw("COLZ0")
    canvas.Update()
    efficiency_TH2D = efficiency_TEff.GetPaintedHistogram()
    efficiency_TH2D.SetName("Efficiency")
    efficiency_TH2D.Scale(100)


    # PROJECTION X AND Y #

    # Set up parameters for the projection objects. Projection Y have same limits to preserve same window
    projectionX_th1d = ROOT.TProfile("Projection X", "projection x", xbin,-sep_x,sep_x)
    
    # Projection Y have extended limits (with larger bin number) to preserve the same length of the window,
    # for better comparison with projection X. The window is then reduced to match the bin number
    projectionY_th1d = ROOT.TProfile("Projection Y", "projection y", xbin,-sep_x,sep_x)
    projectionY_th1d.SetAxisRange(-sep_y, sep_y, "X")

    distance_projection, center_positions = t_calc.findSelectionRange()

    # Define lower and upper limits bins
    bin_x_low = LGAD_th2d.GetXaxis().FindBin(distance_projection[0][0])
    bin_x_high = LGAD_th2d.GetXaxis().FindBin(distance_projection[0][1])
    bin_y_low = LGAD_th2d.GetYaxis().FindBin(distance_projection[1][0])
    bin_y_high = LGAD_th2d.GetYaxis().FindBin(distance_projection[1][1])

    bin_limits = np.array([bin_x_low, bin_x_high, bin_y_low, bin_y_high])


    # Loop through each bin, to obtain inefficiency, and fill projection objects
    for i in range(1, xbin+1): # Avoid underflow and overflow bins!
        for j in range(1, ybin+1): # Avoid underflow and overflow bins!
            
            bin = efficiency_TH2D.GetBin(i,j)
            eff = efficiency_TH2D.GetBinContent(bin)
        
            if eff > 0:
                inefficiency_TH2D.SetBinContent(bin, 100-eff)
            
            if eff == 100:
                inefficiency_TH2D.SetBinContent(bin, 0.001)
    
            # Fill projection Y efficiency values within x-limits
            if bin_limits[0] <= i <= bin_limits[1]:
                y = LGAD_th2d.GetYaxis().GetBinCenter(j)
                projectionY_th1d.Fill(y, eff)

            # Fill projection X efficiency values within y-limits
            if bin_limits[2] <= j <= bin_limits[3]:
                x = LGAD_th2d.GetXaxis().GetBinCenter(i)
                projectionX_th1d.Fill(x, eff)

    # Additional comment: bin_limits marks the lines for which the selection of the
    # projection for each dimension. Vertical limits are for the Y-projection, where
    # horizontal is for X-projection. Then for each "line of bins" are projected by
    # filling within the limits. TProfile objects then calculate the mean in each filled
    # line. The point here is to see how the edges increases

    efficiency_TH2D.SetAxisRange(percentage_efficiency, 100, "Z")
    printTHPlot(efficiency_TH2D, totalEntries)
    
    inefficiency_TH2D.SetAxisRange(0, 100-percentage_efficiency, "Z")
    printTHPlot(inefficiency_TH2D, totalEntries)


    # Create projection plots for single pad only
    produceProjectionPlots(projectionX_th1d, projectionY_th1d, center_positions)

    del LGAD_th2d, MIMOSA_th2d, efficiency_TEff, inefficiency_TH2D, projectionX_th1d, projectionY_th1d




###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def createArrayPadGraphs():

    global chan
    
    [sep_x, sep_y, entries_per_bin, bin_size, minEntries, bin_timing_decrease, peak_value_max, rise_time_max, timing_res_max, gain_max, n_div, max_factor_filling, width_time_diff, percentage_efficiency] = [i for i in glob_variables]
 
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
    timing_cfd_th2d = ROOT.TH2D("Timing resolution cfd", "timing resolution cfd", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    
    efficiency_TH2D = ROOT.TH2D("Efficiency", "Efficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    inefficiency_TH2D = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    TH2D_objects_list = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd_th2d, efficiency_TH2D, inefficiency_TH2D]

    print "\nArray Pad", md.getNameOfSensor(chan), "\n"
    
    for TH2D_object in TH2D_objects_list:
        for index in range(0, len(arrayPadChannels)):
         
            t_calc.importAndAddHistogram(TH2D_object, index)


    # Change the file names of the exported files (array)
    t_calc.setArrayPadExportBool(True)
    chan = t_calc.getArrayPadChannels()[0]
    

    limits = [peak_value_max, rise_time_max, timing_res_max, gain_max,0,0, percentage_efficiency]

    setPlotLimitsAndPrint(TH2D_objects_list, limits)

    for TH2D_object in TH2D_objects_list:
        del TH2D_object



###########################################
#                                         #
#          PROJECTION FUNCTIONS           #
#                                         #
###########################################


def produceProjectionPlots(projectionX_th1d, projectionY_th1d, center_positions):

    # Extend the projection y window, if not in an array pad.
    if not md.checkIfArrayPad(chan):
        projectionY_th1d.SetAxisRange(-glob_variables[0], glob_variables[0], "X")

    headTitle = "Projection of X-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+ "; X [\mum] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    sigmas = createProjectionFit(projectionX_th1d, center_positions[0])
    printProjectionPlot(projectionX_th1d, headTitle, fileName, sigmas)
    
    
    headTitle = headTitle.replace("X-axis", "Y-axis")
    headTitle = headTitle.replace("X [\mum]", "Y [\mum]")
    fileName = fileName.replace("projectionX", "projectionY")
    
    sigmas = createProjectionFit(projectionY_th1d, center_positions[1])
    printProjectionPlot(projectionY_th1d, headTitle, fileName, sigmas)


def createProjectionFit(projection_th1d, center_position):

    separation_distance = 600
    approx_width_projection = 10
    amplitude_efficiency = 100

    formula_fit_left = "[0]*(1/(1+TMath::Exp(([1]-x)/[2)))"
    formula_fit_right = "[0]*(1/(1+TMath::Exp((x-[1])/[2])))"
    
    # Left and right limits for the sensor
    left_position = center_position - separation_distance
    right_position = center_position + separation_distance

    # Start parameters for the sigmoid fit
    formula_fit_left = "[0]*(1/(1+TMath::Exp(([1]-x)/[2)))"
    formula_fit_right = "[0]*(1/(1+TMath::Exp((x-[1])/[2])))"


    fit_sigmoid_left = ROOT.TF1("sigmoid_left", formula_fit_left, left_position, center_position)
    fit_sigmoid_left.SetParameters(amplitude_efficiency, left_position, approx_width_projection)
    
    fit_sigmoid_right = ROOT.TF1("sigmoid_right", formula_fit_right, center_position, right_position)
    fit_sigmoid_right.SetParameters(amplitude_efficiency, right_position, approx_width_projection)
    
    projection_th1d.Fit("sigmoid_left", "QR")
    projection_th1d.Fit("sigmoid_right", "QR+")
    
    projection_th1d.GetFunction("sigmoid_right").SetLineColor(3)
    
    sigma_left          = projection_th1d.GetFunction("sigmoid_left").GetParameter(2)
    sigma_left_error    = projection_th1d.GetFunction("sigmoid_left").GetParError(2)
    sigma_right         = projection_th1d.GetFunction("sigmoid_right").GetParameter(2)
    sigma_right_error   = projection_th1d.GetFunction("sigmoid_right").GetParError(2)

    return [sigma_left, sigma_left_error, sigma_right, sigma_right_error]


###########################################
#                                         #
#        PRINT FUNCTIONS GRAPHS           #
#                                         #
###########################################


def setPlotLimitsAndPrint(TH2D_objects, limits):


    [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd_th2d, efficiency_TH2D, inefficiency_TH2D] = [i for i in TH2D_objects]
    
    [peak_value_max, rise_time_max, timing_res_max, gain_max, time_diff_peak_entries, time_diff_cfd_entries, percentage_efficiency] = [i for i in limits]

    # Print pulse amplitude mean value 2D plot

    # Here import the result from the earlier analysis and center the Z-axis with +-50 mV
    peak_value_mpv = (dm.exportImportROOTData("results", "peak_value", False, "", chan))[0][0]
    peak_value_separation = 50

    peak_value_mean_th2d.SetAxisRange(peak_value_mpv-peak_value_separation, peak_value_mpv+peak_value_separation, "Z")
    peak_value_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(peak_value_mean_th2d)

    # Print gain mean value 2D plot

    # Here import the result from the earlier analysis and center the Z-axis with +-10
    MIP_charge = 0.46 # note that charge is in fC
    gain_mpv = (dm.exportImportROOTData("results", "charge", False, "", chan))[0][0]/MIP_charge
    gain_separation = 20

    gain_mean_th2d.SetAxisRange(gain_mpv-gain_separation, gain_mpv+gain_separation, "Z")
    gain_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(gain_mean_th2d)


    # Print rise time mean value 2D plot
    
    # Import rise time mean result.
    # Here import the result from the earlier analysis and center the Z-axis with +-50 ps
    rise_time_mean_result = (dm.exportImportROOTData("results", "rise_time", False, "", chan))[0][0]
    rise_time_separation = 50

    rise_time_mean_th2d.SetAxisRange(rise_time_mean_result-rise_time_separation, rise_time_mean_result+rise_time_separation, "Z")
    rise_time_mean_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(rise_time_mean_th2d)

    # Print time resolution peak reference
    timing_peak_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_peak_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_peak_th2d, time_diff_peak_entries)


    # Print time resolution cfd ref
    timing_cfd_th2d.SetAxisRange(0, timing_res_max, "Z")
    timing_cfd_th2d.SetNdivisions(n_div, "Z")
    printTHPlot(timing_cfd_th2d, time_diff_cfd_entries)
    
    # In case of array pads, the efficiency plots have already been produced
    if t_calc.array_pad_export:
    
        # Print efficiency plot
        efficiency_TH2D.SetAxisRange(percentage_efficiency, 100, "Z")
        printTHPlot(efficiency_TH2D)

        # Print inefficiency plots
        inefficiency_TH2D.SetAxisRange(0, 100-percentage_efficiency, "Z")
        printTHPlot(inefficiency_TH2D)


# Print TH2 Object plot
def printTHPlot(graphList, entries=0):
    
    canvas.cd()
    
    if entries == 0:
        entries = graphList.GetEntries()
    
    # Get file name and title for graph
    objectName = graphList.GetName()
    fileName, headTitle = t_calc.getTitleAndFileName(objectName, chan)

    # Move the right margin to fit the Z axis
    canvas.SetRightMargin(0.14)

    # Draw graph to move and recreate the stats box
    graphList.SetStats(1)
    graphList.Draw("COLZ0")
    canvas.Update()
    stats_box = graphList.GetListOfFunctions().FindObject("stats")
    stats_box.SetX1NDC(.1)
    stats_box.SetX2NDC(.25)
    stats_box.SetY1NDC(.9)
    stats_box.SetY2NDC(.83)
    stats_box.SetOptStat(1000000010)
    graphList.SetEntries(entries)
    
    # Draw again to update the canvas
    graphList.SetTitle(headTitle)
    graphList.Draw("COLZ0")

    # Draw lines which selects the projection limits
    efficiency = False if objectName.find("Efficiency") == -1 else True
    lines = t_calc.drawLines(efficiency)
    
#    # Select which lines to draw
#    if efficiency:
#        lines[0].Draw()
#        lines[1].Draw()
#        lines[2].Draw()
#        lines[3].Draw()
        

    # Export PDF and Histogram
    canvas.Print(fileName)
    dm.exportImportROOTHistogram(fileName, True, graphList)
    canvas.Clear()


# Print projection plot
def printProjectionPlot(th1_projection, headTitle, fileName, sigmas):

    canvas_projection.cd()

    ROOT.gStyle.SetOptStat("e")
    ROOT.gStyle.SetOptFit(0)

    th1_projection.SetTitle(headTitle)
    th1_projection.Draw()
    canvas_projection.Update()

    # Remove text from stats box
    stats_box = canvas_projection.GetPrimitive("stats")
    stats_box.SetName("Mystats")
    th1_projection.SetStats(0)
    stats_box.SetX1NDC(.79)
    stats_box.SetX2NDC(.98)
    stats_box.SetY1NDC(.9)
    stats_box.SetY2NDC(.73)
    stats_box.AddText("\sigma_{left} = "+str(sigmas[0])[0:5] + " \pm " + str(sigmas[1])[0:4])
    stats_box.AddText("\sigma_{right} = "+str(sigmas[2])[0:5] + " \pm " + str(sigmas[3])[0:4])
    canvas_projection.Modified()
    canvas_projection.Update()
    
    
    # Export PDF
    canvas_projection.Print(fileName)
    
    # Export histogram as ROOT file
    dm.exportImportROOTHistogram(fileName, True, th1_projection)
    canvas_projection.Clear()
    
