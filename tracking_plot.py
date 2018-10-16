import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_calculations as t_calc

ROOT.gROOT.SetBatch(True)

n_div = 10                  # Number of ticks on Z-axis
percentage_efficiency = 80  # Limit the lower percentage
timing_res_max = 100        # Z-axis limit for timing resolution graph
peak_value_max = 400        # Z-axis limit for pulse amplitude graph
gain_max = 160              # Z-axis limit for gain graph
rise_time_max = 1000        # Z-axis limit for rise time graph

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(5*n_div)

def trackingPlots(numpy_arrays):
    #def trackingPlots(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking):
   
    [peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking] = [i for i in numpy_arrays]
   
    global canvas, canvas_projection
    global glob_variables

    distance_x = 800 # Width from the center of the canvas in x default 800
    distance_y = 600 # Width from the center of the canvas in y default 600
    
    bin_size = 18.5 # Pixel size from the MIMOSA
    bin_entries = 5 # Minimum entries per bin
    
    bin_entries_timing = 50 # Required entries for timing resolution graphs
    bin_timing_decrease = 3 # Bin size increase to adapt for timing resolution plots
    width_time_diff = 500 # Width from the mean value of filling time difference values, this is to exclude extreme values
    
    glob_variables = [distance_x, distance_y, bin_entries_timing, bin_size, bin_entries, bin_timing_decrease, width_time_diff]
    
    t_calc.setArrayPadExportBool(False)
    
    canvas = ROOT.TCanvas("Tracking", "tracking")
    canvas_projection = ROOT.TCanvas("Projection", "projection")
    
    # Convert pulse amplitude values from [-V] to [+mV], charge from [C] to gain, rise time from [ns] to [ps]
    dm.changeIndexNumpyArray(peak_values, -1000)
    dm.changeIndexNumpyArray(gain, 1./(0.46*10**-15))
    dm.changeIndexNumpyArray(rise_times, 1000)

    createSinglePadGraphs(peak_values, gain, rise_times, time_difference_peak, time_difference_cfd, tracking)

    # Create array pad graphs for all batches
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
    
        md.setChannelName(chan)
        
        if (md.getSensor() != md.sensor and md.sensor != "") or md.getSensor() == "SiPM-AFP":
            continue
    
        print "\nSingle pad", md.getSensor(), "\n"

        # This function requires a ROOT file which have the center positions for each pad
        tracking_chan = t_calc.changeCenterPositionSensor(np.copy(tracking))

        produceTProfilePlots([peak_values[chan], gain[chan], rise_times[chan], time_difference_peak[chan], time_difference_cfd[chan]], tracking_chan)
        produceEfficiencyPlot(peak_values[chan], tracking_chan)


###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def createArrayPadGraphs():
    
    global chan
    
    [distance_x, distance_y, bin_entries_timing, bin_size, bin_entries, bin_timing_decrease, width_time_diff] = [i for i in glob_variables]
 
    distance_x *= 2
    distance_y *= 2
    
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)
    
    # The binning for the timing resolution is decreased
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    arrayPadChannels = t_calc.getArrayPadChannels()
    
    chan = arrayPadChannels[0]
    md.setChannelName(chan)


    peak_value_mean_th2d = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    gain_mean_th2d = ROOT.TProfile2D("Gain mean value","Gain mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    rise_time_mean_th2d = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    
    timing_peak_th2d = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    timing_cfd_th2d = ROOT.TH2D("Timing resolution cfd", "timing resolution cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    
    efficiency_TH2D = ROOT.TH2D("Efficiency", "Efficiency",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    inefficiency_TH2D = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    TH2D_objects_list = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd_th2d, efficiency_TH2D, inefficiency_TH2D]

    print "\nArray Pad", md.getSensor(), "\n"
    
    for TH2D_object in TH2D_objects_list:
        for index in range(0, len(arrayPadChannels)):
         
            t_calc.importAndAddHistogram(TH2D_object, index)


    # Change the file names of the exported files (array)
    t_calc.setArrayPadExportBool(True)

    setPlotLimitsAndPrint(TH2D_objects_list)



#########################################################
#                                                       #
#   GAIN, PULSE MEAN VALUE AND TIME RESOLUTION GRAPHS   #
#                                                       #
#########################################################


# Produce mean value and time resolution plots
def produceTProfilePlots(numpy_arrays, tracking):
    
    [distance_x, distance_y, bin_entries_timing, bin_size, bin_entries, bin_timing_decrease, width_time_diff] = [i for i in glob_variables]
    

    if md.checkIfArrayPad():
    
        distance_x *= 2
        distance_y *= 2
    
    # Adaptive bin number
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)
    
    # Decreased number of bins for timing resolution plots
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    # Import values mean values of the time difference.
    mpv_time_diff_peak =  dm.exportImportROOTData("results", "linear")["linear"][2]
    mpv_time_diff_cfd  =  dm.exportImportROOTData("results", "linear_cfd")["linear_cfd"][2]

    # Declare ROOT objects
    peak_value_mean_th2d        = ROOT.TProfile2D("Pulse amplitude mean value","Pulse amplitude mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    gain_mean_th2d              = ROOT.TProfile2D("Gain mean value","Gain mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    rise_time_mean_th2d         = ROOT.TProfile2D("Rise time mean value","Rise time mean value", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    
    time_difference_peak_th2d   = ROOT.TProfile2D("Time difference peak", "Time difference peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y, "s")
    time_difference_cfd_th2d    = ROOT.TProfile2D("Time difference cfd", "Time difference cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y, "s")
    timing_peak_th2d            = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    timing_cfd_th2d             = ROOT.TH2D("Timing resolution cfd", "timing resolution cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    
    TH2_objects_fill = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, time_difference_peak_th2d, time_difference_cfd_th2d]
    
    
    fill = False
    # Fill all objects except timing resolution
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):
            for index in range(0, len(numpy_arrays)):
                if numpy_arrays[index][event] != 0:
                    if index == 3:
                        if (mpv_time_diff_peak - width_time_diff) < numpy_arrays[index][event] < (mpv_time_diff_peak + width_time_diff):
                            fill = True
                    elif index == 4:
                        if (mpv_time_diff_cfd - width_time_diff) < numpy_arrays[index][event] < (mpv_time_diff_cfd + width_time_diff):
                            fill = True
                    else:
                        fill = True
                    
                    if fill:
                        TH2_objects_fill[index].Fill(tracking['X'][event], tracking['Y'][event], numpy_arrays[index][event])
                        fill = False


    # Remove bins with few entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = peak_value_mean_th2d.GetBin(i,j)
            t_calc.removeBin(bin, peak_value_mean_th2d, bin_entries)
            t_calc.removeBin(bin, rise_time_mean_th2d, bin_entries)
            t_calc.removeBin(bin, gain_mean_th2d, bin_entries)

    peak_value_mean_th2d.ResetStats()
    rise_time_mean_th2d.ResetStats()
    gain_mean_th2d.ResetStats()

    # Fill timing resolution bins
    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
        
            bin = time_difference_peak_th2d.GetBin(i,j)
            t_calc.fillTimeResBin(bin, time_difference_peak_th2d, timing_peak_th2d, bin_entries_timing)
            t_calc.fillTimeResBin(bin, time_difference_cfd_th2d, timing_cfd_th2d, bin_entries_timing)


    # Print pulse amplitude mean value 2D plot
    TH2D_objects = [peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, timing_peak_th2d, timing_cfd_th2d, 0, 0]
    limits = [time_difference_peak_th2d.GetEntries(), time_difference_cfd_th2d.GetEntries()]
    setPlotLimitsAndPrint(TH2D_objects, limits)

    del peak_value_mean_th2d, gain_mean_th2d, rise_time_mean_th2d, time_difference_peak_th2d, time_difference_cfd_th2d, timing_peak_th2d, timing_cfd_th2d


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking):

    [distance_x, distance_y, bin_entries_timing, bin_size, bin_entries, bin_timing_decrease, width_time_diff] = [i for i in glob_variables]
    
    if md.checkIfArrayPad():
    
        distance_x *= 2
        distance_y *= 2

    # Define how many bins to use for the TH2-objects
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)

    # Fill events for which the sensors records a hit
    LGAD_th2d         = ROOT.TH2D("LGAD_particles", "LGAD particles",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA_th2d       = ROOT.TH2D("tracking_particles", "Tracking particles",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    
    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):
    
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

            if num_LGAD < bin_entries:
                LGAD_th2d.SetBinContent(bin, 0)
                MIMOSA_th2d.SetBinContent(bin, 0)


    LGAD_th2d.ResetStats()
    MIMOSA_th2d.ResetStats()
    
    # Create efficiency and inefficiency objects
    efficiency_TEff = ROOT.TEfficiency(LGAD_th2d, MIMOSA_th2d)
    inefficiency_TH2D = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)

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
    projectionX_th1d = ROOT.TProfile("Projection X", "projection x", xbin,-distance_x,distance_x)
    
    # Projection Y have extended limits (with larger bin number)
    # to preserve the same length of the window, for better comparison with projection X.
    # The window is then reduced to match the bin number
    projectionY_th1d = ROOT.TProfile("Projection Y", "projection y", xbin,-distance_x,distance_x)

    distance_projection, center_positions = t_calc.findSelectionRange()
    
    # For fun, introduce a circular area

    # Define lower and upper limits bins
    bin_x_low = LGAD_th2d.GetXaxis().FindBin(distance_projection[0][0])
    bin_x_high = LGAD_th2d.GetXaxis().FindBin(distance_projection[0][1])
    bin_y_low = LGAD_th2d.GetYaxis().FindBin(distance_projection[1][0])
    bin_y_high = LGAD_th2d.GetYaxis().FindBin(distance_projection[1][1])

    bin_limits = np.array([bin_x_low, bin_x_high, bin_y_low, bin_y_high])
    
    efficiency_bulk_data = np.array([])

    # Loop through each bin, to obtain inefficiency, and fill projection objects
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = efficiency_TH2D.GetBin(i,j)
            eff = efficiency_TH2D.GetBinContent(bin)
        
            if eff > 0:
                inefficiency_TH2D.SetBinContent(bin, 100-eff)
            
                if (bin_limits[0] <= i <= bin_limits[1]) and (bin_limits[2] <= j <= bin_limits[3]):
  
                    efficiency_bulk_data = np.concatenate((efficiency_bulk_data, np.array([eff])))
            
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



    efficiency_bulk = [np.mean(efficiency_bulk_data), np.std(efficiency_bulk_data)]
    dm.exportImportROOTData("tracking", "efficiency", np.array(efficiency_bulk))

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
#          PROJECTION FUNCTIONS           #
#                                         #
###########################################


def produceProjectionPlots(projectionX_th1d, projectionY_th1d, center_positions):

    headTitle = "Projection of X-axis of efficiency 2D plot - "+md.getSensor()+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"+ "; X [\mum] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/"+md.getSensor()+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getSensor())+".pdf"

    
    sigmas = createProjectionFit(projectionX_th1d, center_positions[0])
    printProjectionPlot(projectionX_th1d, headTitle, fileName, sigmas)
   
    headTitle = headTitle.replace("X-axis", "Y-axis")
    headTitle = headTitle.replace("X [\mum]", "Y [\mum]")
    fileName = fileName.replace("projectionX", "projectionY")
    
    sigmas = createProjectionFit(projectionY_th1d, center_positions[1])
    printProjectionPlot(projectionY_th1d, headTitle, fileName, sigmas)


def createProjectionFit(projection_th1d, center_position):
    
    separation_distance = 600
    approx_steepness = 10
    amplitude_efficiency = 100
    
    # Left and right limits for the sensor
    left_position = center_position - separation_distance
    right_position = center_position + separation_distance

    fit_sigmoid_left = ROOT.TF1("sigmoid_left", "[0]/(1+TMath::Exp(([1]-x)/[2]))", left_position, center_position)
    fit_sigmoid_left.SetParameters(amplitude_efficiency, left_position, approx_steepness)
    
    fit_sigmoid_right = ROOT.TF1("sigmoid_right", "[0]/(1+TMath::Exp((x-[1])/[2]))", center_position, right_position)
    fit_sigmoid_right.SetParameters(amplitude_efficiency, right_position, approx_steepness)
    
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


def setPlotLimitsAndPrint(TH2D_objects, timing_entries=[0,0]):

    limits_graph = [peak_value_max, gain_max, rise_time_max, timing_res_max, timing_res_max]
    entries = [0, 0, 0, timing_entries[0], timing_entries[1]]
    
    for index in range(0, len(limits_graph)):
        TH2D_objects[index].SetAxisRange(0, limits_graph[index], "Z")
        TH2D_objects[index].SetNdivisions(n_div, "Z")
        printTHPlot(TH2D_objects[index], entries[index])


    # Export efficiency graphs for array pads (the single ones have already been exported at this point)
    if t_calc.array_pad_export:

        # Print efficiency plot
        TH2D_objects[-2].SetAxisRange(percentage_efficiency, 100, "Z")
        printTHPlot(TH2D_objects[-2])

        # Print inefficiency plots
        TH2D_objects[-1].SetAxisRange(0, 100-percentage_efficiency, "Z")
        printTHPlot(TH2D_objects[-1])


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
    stats_box.SetY1NDC(.93)
    stats_box.SetY2NDC(.83)
    stats_box.SetOptStat(1000000010)
    graphList.SetEntries(entries)


    # Draw again to update the canvas
    graphList.SetTitle(headTitle)
    graphList.Draw("COLZ0")

    # Draw lines which selects the projection limits
    efficiency_bool = False if objectName.find("Efficiency") == -1 else True

    if efficiency_bool:
    
        # This prints the selections for the efficiency bulk calculations
        if md.checkIfArrayPad() and t_calc.array_pad_export:
            channels = t_calc.getArrayPadChannels()
        
        else:
            channels = [md.chan_name]
    
        lines = dict()
        efficiency_text = dict()
    
        for chan_2 in channels:
        
            md.setChannelName(chan_2)
            
            lines[chan_2] = t_calc.drawLines(0) # the argument extends the lines
            limits, center_position = t_calc.findSelectionRange()
            
            efficiency_bulk = dm.exportImportROOTData("tracking", "efficiency")
            
            efficiency_text[chan_2] = ROOT.TLatex(center_position[0]-250,center_position[1],  "Eff = " + str(efficiency_bulk[chan_2][0])[0:5] + " \pm " + str(efficiency_bulk[chan_2][1])[0:4] + " %")

            efficiency_text[chan_2].SetNDC(False)
            if md.checkIfArrayPad():
                efficiency_text[chan_2].SetTextSize(0.02)
            else:
                efficiency_text[chan_2].SetTextSize(0.04)
            efficiency_text[chan_2].Draw()

            # Draw lines which marks the bulk
            # Comment to draw selected lines
            lines[chan_2][0].Draw()
            lines[chan_2][1].Draw()
            lines[chan_2][2].Draw()
            lines[chan_2][3].Draw()
            
            canvas.Update()



    # Export PDF and Histogram
    canvas.Update()
    canvas.Print(fileName)
    dm.exportImportROOTHistogram(fileName, graphList)
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
    dm.exportImportROOTHistogram(fileName, th1_projection)
    canvas_projection.Clear()
    
