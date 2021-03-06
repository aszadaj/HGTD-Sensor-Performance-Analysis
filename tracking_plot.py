import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_calculations as t_calc

ROOT.gROOT.SetBatch(True)

distance_x = 800 # Width from the center of the canvas in x default 800
distance_y = 600 # Width from the center of the canvas in y default 600

n_div = 10                      # Number of ticks on Z-axis
percentage_efficiency = 80      # Limit the lower percentage

min_entries_bin = 5             # Minimum entries per bin
min_entries_bin_timing = 50     # Required entries for timing resolution graphs
pixel_size = 18.4               # Pixel size for the MIMOSA
bin_size_increase_timing = 2.5  # Bin size increase to adapt for timing resolution plots


ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(10*n_div)


# Function appends tracking files and oscilloscope files and
# matches the sizes of them
def trackingPlots():
    
    global var_names
    
    startTime = dm.getTime()
    
    print "\nStart TRACKING analysis, batches:", md.batchNumbers, "\n"
    
    for batchNumber in md.batchNumbers:
        
        startTimeBatch = dm.getTime()
        runNumbers = md.getAllRunNumbers(batchNumber)
        
        # Omit batches with less than 3 runs
        if len(runNumbers) < 3:
            
            print "Batch", batchNumber, "omitted, < 3 runs.\n"
            continue
        
        print "BATCH", batchNumber, "\n"
    
        var_names = [["pulse", "pulse_amplitude"], ["pulse", "charge"], ["pulse", "rise_time"], ["timing", "normal_peak"], ["timing", "normal_cfd"]]
        
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(len(var_names))]
        numpy_arrays.append(np.empty(0, dtype = dm.getDTYPETracking()))
        
        max_sample = np.empty(0, dtype = dm.getDTYPE(batchNumber))
        
        for runNumber in runNumbers:
            
            md.defineRunInfo(md.getRowForRunNumber(runNumber))
            
            # Produce timing resolution files if they not exist
            if not dm.checkIfROOTDataFileExists("timing", "normal_peak"):
                t_calc.createTimingFiles(batchNumber)
            
            if not dm.checkIfFileAvailable("tracking"):
                continue
        
            tracking_run = dm.exportImportROOTData("tracking", "tracking")
            
            # This strips the event number to match the ones with the tracking. It assumes that the tracking have fewer number of events than the oscilloscope events.
            for index in range(0, len(var_names)):
                numpy_arrays[index] = np.concatenate((numpy_arrays[index], np.take(dm.exportImportROOTData(var_names[index][0], var_names[index][1]), np.arange(0, len(tracking_run)))), axis=0)
            
            max_sample = np.concatenate((max_sample, np.take(dm.exportImportROOTData("pulse", "max_sample"), np.arange(0, len(tracking_run)))), axis=0)
            
            
            # Concatenate tracking arrays
            numpy_arrays[-1] = np.concatenate((numpy_arrays[-1], tracking_run), axis=0)
    
    
        [pulse_amplitude, gain, rise_time, time_difference_peak, time_difference_cfd, tracking] = [i for i in numpy_arrays]
        
        # This checks if the position file exists, otherwise it will create it
        if not dm.checkIfROOTDataFileExists("tracking", "position"):
            t_calc.calculateCenterOfSensorPerBatch(pulse_amplitude, tracking)
    
        declareTCanvas()
        defineBinSizes()

        if md.getBatchNumber()/100 == 7:
            updateBinSize(1.5)

        t_calc.setArrayPadExportBool(False)

        createSinglePadGraphs(numpy_arrays, max_sample)
        
        createArrayPadGraphs(distance_x, distance_y)
        
        print "\nDone with batch", batchNumber, "Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"
                                
                                
    print "\nDone with TRACKING analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"


###########################################
#                                         #
#           SINGLE PAD GRAPHS             #
#                                         #
###########################################



def createSinglePadGraphs(numpy_arrays, max_sample):
    
    [pulse_amplitude, gain, rise_time, time_difference_peak, time_difference_cfd, tracking] = [i for i in numpy_arrays]
    
    # Convert pulse amplitude values from [-V] to [+mV], charge from [C] to gain, rise time from [ns] to [ps]
    dm.changeIndexNumpyArray(pulse_amplitude, -1000.0)
    dm.changeIndexNumpyArray(max_sample, -1000.0)
    dm.changeIndexNumpyArray(gain, 1./(md.getChargeWithoutGainLayer()*10**-15))
    dm.changeIndexNumpyArray(rise_time, 1000.0)
    
    # Produce single pad plots
    for chan in pulse_amplitude.dtype.names:
    
        md.setChannelName(chan)
        
        if (md.getSensor() != md.sensor and md.sensor != "") or md.getSensor() == "SiPM-AFP":
            continue

        print "Single pad", md.getSensor(), "\n"

        # This function requires a ROOT file which have the center positions for each pad
        tracking_chan = t_calc.changeCenterPositionSensor(np.copy(tracking))
        
        produceTProfilePlots([np.copy(pulse_amplitude[chan]), gain[chan], rise_time[chan], time_difference_peak[chan], time_difference_cfd[chan]], max_sample[chan], tracking_chan, distance_x, distance_y)
        produceEfficiencyPlot(pulse_amplitude[chan], tracking_chan, distance_x, distance_y)



#####################################################################
#                                                                   #
#    PULSE AMPLITUDE, RISE TIME, GAIN AND TIME RESOLUTION GRAPHS    #
#                                                                   #
#####################################################################


# Produce mean value and time resolution plots
def produceTProfilePlots(numpy_arrays, max_sample, tracking, distance_x, distance_y):
    
    if md.checkIfArrayPad():
        
        distance_x *= 2
        distance_y *= 2
    
    # Adaptive bin number
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)
    
    # Decreased number of bins for timing resolution plots
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)

    th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
    
    # Declare ROOT objects
    pulse_amplitude_TH2D   = ROOT.TProfile2D("pulse_amplitude"+th_name, "pulse_amplitude", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    gain_TH2D              = ROOT.TProfile2D("gain"+th_name,"gain", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    rise_time_TH2D         = ROOT.TProfile2D("rise_time"+th_name,"rise_time", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    
    timing_peak_TH2D       = ROOT.TH2D("timing_peak"+th_name, "timing_peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    timing_cfd_TH2D        = ROOT.TH2D("timing_cfd"+th_name, "timing_cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    
    TH2_pulse = [pulse_amplitude_TH2D, gain_TH2D, rise_time_TH2D]
    TH2_timing = [timing_peak_TH2D, timing_cfd_TH2D]
    entries_timing_resolution = t_calc.fillTHObjects(numpy_arrays, max_sample, TH2_pulse, TH2_timing, tracking, [xbin, ybin, xbin_timing, ybin_timing, distance_x, distance_y])
  
    # Print pulse amplitude mean value 2D plot
    TH2D_objects = [pulse_amplitude_TH2D, gain_TH2D, rise_time_TH2D, timing_peak_TH2D, timing_cfd_TH2D, 0, 0]
    setPlotLimitsAndPrint(TH2D_objects, entries_timing_resolution)



###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (for each pad)
def produceEfficiencyPlot(pulse_amplitude, tracking, distance_x, distance_y):
    
    if md.checkIfArrayPad():
    
        distance_x *= 2
        distance_y *= 2

    # Define how many bins to use for the TH2-objects
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)

    # Fill events for which the sensors records a hit
    LGAD_TH2D         = ROOT.TH2D("LGAD_particles", "LGAD particles",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA_TH2D       = ROOT.TH2D("tracking_particles", "Tracking particles",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    t_calc.fillEfficiencyObjects(LGAD_TH2D, MIMOSA_TH2D, tracking, pulse_amplitude, distance_x, distance_y, xbin, ybin)

    # Create efficiency and inefficiency objects
    th_name = "_" + str(md.getBatchNumber()) + "_" + md.chan_name
    efficiency_TEff = ROOT.TEfficiency(LGAD_TH2D, MIMOSA_TH2D)
    inefficiency_TH2D = ROOT.TH2D("inefficiency"+th_name, "inefficiency",xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)

    # Total entries refer to pass events, that is number of recorded pixels on the sensor given a hit
    # in the MIMOSA. This number is used for both efficiency and inefficiency plots.
    totalEntries = efficiency_TEff.GetPassedHistogram().GetEntries()

    # Draw the TEfficiency object, and rescale it
    efficiency_TEff.Draw("COLZ0")
    canvas.Update()
    efficiency_TH2D = efficiency_TEff.GetPaintedHistogram()
    efficiency_TH2D.SetName("efficiency"+th_name)
    efficiency_TH2D.SetTitle("efficiency")
    efficiency_TH2D.Scale(100)

    # PROJECTION X AND Y #
    
    # Projection Y have extended limits (with larger bin number)
    # to preserve the same length of the window, for better comparison with projection X.
    # The window is then reduced to match the bin number
    
    projectionX_th1d = ROOT.TProfile("projection_x"+th_name, "projection_x", xbin,-distance_x,distance_x)
    projectionY_th1d = ROOT.TProfile("projection_y"+th_name, "projection_y", xbin,-distance_x,distance_x)
    
    t_calc.fillInefficiencyAndProjectionObjects(efficiency_TH2D, inefficiency_TH2D, projectionX_th1d, projectionY_th1d, xbin, ybin)

    efficiency_TH2D.SetAxisRange(percentage_efficiency, 100, "Z")
    printTHPlot(efficiency_TH2D, totalEntries)
    
    inefficiency_TH2D.SetAxisRange(0, 100-percentage_efficiency, "Z")
    printTHPlot(inefficiency_TH2D, totalEntries)

    # Create projection plots for single pad only
    produceProjectionPlots(projectionX_th1d, projectionY_th1d)



###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def createArrayPadGraphs(distance_x, distance_y):
    
    if not t_calc.sensorIsAnArrayPad():
        return 0
    
    distance_x *= 2
    distance_y *= 2
    
    xbin = int(2*distance_x/bin_size)
    ybin = int(2*distance_y/bin_size)
    
    # The binning for the timing resolution is decreased
    xbin_timing = int(xbin/bin_timing_decrease)
    ybin_timing = int(ybin/bin_timing_decrease)
    
    arrayPadChannels = t_calc.getArrayPadChannels()
    md.setChannelName(arrayPadChannels[0])
    
    th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
    
    pulse_amplitude_TH2D   = ROOT.TProfile2D("pulse_amplitude"+th_name, "pulse_amplitude", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    gain_TH2D              = ROOT.TProfile2D("gain"+th_name, "gain", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    rise_time_TH2D         = ROOT.TProfile2D("rise_time"+th_name, "rise_time", xbin, -distance_x, distance_x, ybin, -distance_y, distance_y)
    
    timing_peak_TH2D       = ROOT.TH2D("timing_peak"+th_name, "timing_peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    timing_cfd_TH2D        = ROOT.TH2D("timing_cfd"+th_name, "timing_cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y)
    
    efficiency_TH2D        = ROOT.TH2D("efficiency"+th_name, "efficiency", xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    inefficiency_TH2D      = ROOT.TH2D("inefficiency"+th_name, "inefficiency", xbin,-distance_x,distance_x,ybin,-distance_y,distance_y)
    
    TH2D_objects_list = [pulse_amplitude_TH2D, gain_TH2D, rise_time_TH2D, timing_peak_TH2D, timing_cfd_TH2D, efficiency_TH2D, inefficiency_TH2D]
    
    print "\nArray-pad", md.getSensor(), "\n"
    
    for TH2D_object in TH2D_objects_list:
        for index in range(0, len(arrayPadChannels)):
            
            # Omit the lower-left pad for timing resolution only for W4-S215 B207 Sep TB17
            if TH2D_object.GetName().find("timing") != -1 and arrayPadChannels[index] == "chan3":
                continue

            t_calc.importAndAddHistogram(TH2D_object, index)


    # Change the file names of the exported files (array)
    t_calc.setArrayPadExportBool(True)

    setPlotLimitsAndPrint(TH2D_objects_list)


###########################################
#                                         #
#          PROJECTION FUNCTIONS           #
#                                         #
###########################################


def produceProjectionPlots(projectionX_th1d, projectionY_th1d):
    
    distance_projection, center_positions = t_calc.findSelectionRange()

    headTitle = "Projection on X-axis of efficiency 2D plot - "+md.getSensor()+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"+ "; X [\mum] ; Efficiency (%)"
    
    category = projectionX_th1d.GetTitle()
    fileName = dm.getFileNameForHistogram("tracking", category)

    
    sigmas_x = createProjectionFit(projectionX_th1d, center_positions[0])
    printProjectionPlot(projectionX_th1d, headTitle, fileName, sigmas_x)
   
   
    headTitle = headTitle.replace("X-axis", "Y-axis")
    headTitle = headTitle.replace("X [\mum]", "Y [\mum]")
    
    category = projectionY_th1d.GetTitle()
    fileName = dm.getFileNameForHistogram("tracking", category)

    
    sigmas_y = createProjectionFit(projectionY_th1d, center_positions[1])
    printProjectionPlot(projectionY_th1d, headTitle, fileName, sigmas_y)


def createProjectionFit(projection_th1d, center_position):
    
    separation_distance = 500
    approx_steepness = 10
    amplitude_efficiency = 100
    
    # Left and right limits for the sensor
    left_position = center_position - separation_distance
    right_position = center_position + separation_distance
    
    # Here "left" refers to negative X or Y values
    fit_sigmoid_left = ROOT.TF1("sigmoid_left", "[0]/(1+TMath::Exp(([1]-x)/[2]))", left_position-100, center_position)
    fit_sigmoid_left.SetParameters(amplitude_efficiency, left_position, approx_steepness)
    
    # Here "right" refers to positive X or Y values
    fit_sigmoid_right = ROOT.TF1("sigmoid_right", "[0]/(1+TMath::Exp((x-[1])/[2]))", center_position, right_position+100)
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
    
    # Obtain defined limits
    limits_graph = getLimitsForEachSensorAndBatch()

    # The zeros indicate that the entries are already set for these types of TH-objects
    entries = [0, 0, 0, timing_entries[0], timing_entries[1]]
    
    for index in range(0, len(limits_graph)):
        
        # Set axis ranges for each TH-object
        TH2D_objects[index].SetAxisRange(limits_graph[index][0], limits_graph[index][1], "Z")
        
        # Assign number of divisions for 'Z'-axis label
        TH2D_objects[index].SetNdivisions(n_div, "Z")
        
        # Export the plot
        printTHPlot(TH2D_objects[index], entries[index])


    # Export efficiency graphs for array pads (the mean value graphs have already been exported at this point)
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
    category = graphList.GetTitle()
    headTitle = getTitles(category)

    # Move the margins to fit the Z axis
    canvas.SetRightMargin(0.14)
    canvas.SetLeftMargin(0.11)

    # Draw graph to move and recreate the stats box
    graphList.SetStats(1)
    graphList.Draw("COLZ0")
    canvas.Update()
    stats_box = graphList.GetListOfFunctions().FindObject("stats")
    stats_box.SetX1NDC(.11)
    stats_box.SetX2NDC(.25)
    stats_box.SetY1NDC(.93)
    stats_box.SetY2NDC(.83)
    stats_box.SetOptStat(1000000010)
    graphList.SetEntries(entries)


    # Draw again to update the canvas
    graphList.SetTitle(headTitle)
    graphList.Draw("COLZ0")

    # Draw lines which selects the projection limits
    efficiency_bool = True if category.find("efficiency") != -1 and category.find("inefficiency") == -1 else False

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
            
            lines[chan_2] = t_calc.definelines(0) # the argument extends the lines in [um]
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
            
            # Y-lines
            lines[chan_2][0].Draw()
            lines[chan_2][1].Draw()
            
            # X-lines
            lines[chan_2][2].Draw()
            lines[chan_2][3].Draw()
            
            canvas.Update()


    # Export PDF and Histogram
    canvas.Update()
    subcategory = ""

    if category.find("timing") != -1:
        category, subcategory = category.split("_")

    fileName = dm.getFileNameForHistogram("tracking", category, subcategory)

    canvas.Print(fileName)
    dm.exportImportROOTHistogram("tracking", category, subcategory, "", graphList)
    canvas.Clear()


# Print projection plot
def printProjectionPlot(th1_projection, headTitle, fileName, sigmas):
    
    category = th1_projection.GetTitle()
    
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
    
    text_left = "left"
    text_right = "right"
    
    if th1_projection.GetName().find("y") != -1:
        text_left = "bottom"
        text_right = "top"
    
    
    stats_box.AddText("\sigma_{"+text_left+"} = "+str(sigmas[0])[0:5] + " \pm " + str(sigmas[1])[0:4])
    stats_box.AddText("\sigma_{"+text_right+"} = "+str(sigmas[2])[0:5] + " \pm " + str(sigmas[3])[0:4])
    canvas_projection.Modified()
    canvas_projection.Update()
    
    
    # Export PDF
    canvas_projection.Print(fileName)
    
    # Export histogram as ROOT file
    dm.exportImportROOTHistogram("tracking", category , "", "", th1_projection)
    canvas_projection.Clear()



def declareTCanvas():

    global canvas, canvas_projection
    
    canvas = ROOT.TCanvas("Tracking "+str(md.getBatchNumber()), "tracking")
    canvas_projection = ROOT.TCanvas("Projection "+str(md.getBatchNumber()), "projection")


def defineBinSizes():
    
    global bin_size, bin_entries, bin_entries_timing, bin_timing_decrease

    bin_size = pixel_size
    bin_entries = min_entries_bin
    bin_entries_timing = min_entries_bin_timing
    bin_timing_decrease = bin_size_increase_timing


def updateBinSize(factor):
    
    global bin_size
    
    bin_size *= factor


def getTitles(objectTitle):
    
    headTitle = "empty"
    
    if objectTitle.find("pulse_amplitude") != -1:
        graphTitle = "Pulse amplitude mean value"
        dimension_z = "V [mV]"
    
    
    elif objectTitle.find("gain") != -1:
        graphTitle = "Gain mean value"
        dimension_z = "Gain"
    
    
    elif objectTitle.find("rise_time") != -1:
        graphTitle = "Rise time mean value"
        dimension_z = "t [ps]"
    
    
    elif objectTitle.find("peak") != -1:
        graphTitle = "Timing resolution (peak)"
        dimension_z = "\sigma_{t} [ps]"
    
    
    elif objectTitle.find("cfd") != -1:
        
        graphTitle = "Timing resolution (CFD)"
        dimension_z = "\sigma_{t} [ps]"
    
    
    elif objectTitle.find("efficiency") != -1:
        graphTitle = "Efficiency"
        dimension_z = "Efficiency (%)"
    
    
    elif objectTitle.find("inefficiency") != -1:
        graphTitle = "Inefficiency"
        dimension_z = "Inefficiency (%)"

    headTitle = graphTitle + " - " + md.getSensor() + ", T = " + str(md.getTemperature()) + " \circ C, U = " + str(md.getBiasVoltage()) + " V; X [\mum] ; Y [\mum] ; " + dimension_z

    return headTitle

# These limits are manually adapted for TB Sep 2017
def getLimitsForEachSensorAndBatch():

    if md.getSensor() == "50D-GBGR2" and md.getBatchNumber() == 108:
        
        # not used
        gain_limits = [20, 70]
        pulse_amplitude_limits = [100, 160]
        rise_time_limits = [400, 460]
        
        timing_res_cfd_limits = [22, 40]
        timing_res_peak_limits = [27, 47]
    
    
    elif md.getSensor() == "50D-GBGR2" and md.getBatchNumber() == 207:
        
        gain_limits = [20, 55]
        pulse_amplitude_limits = [80, 150]
        rise_time_limits = [415, 450]
        
        # not used
        timing_res_cfd_limits = [22, 60]
        timing_res_peak_limits = [25, 65]
    
    elif md.getSensor() == "W4-LG12" and md.getBatchNumber() == 108:
        
        # not used
        gain_limits = [20, 90]
        pulse_amplitude_limits = [60, 160]
        rise_time_limits = [520, 560]
        
        timing_res_cfd_limits = [18, 32]
        timing_res_peak_limits = [30, 46]
    
    elif md.getSensor() == "W4-LG12" and md.getBatchNumber() == 207:
        
        gain_limits = [30, 90]
        pulse_amplitude_limits = [60, 155]
        rise_time_limits = [520, 565]
        
        # not used
        timing_res_cfd_limits = [20, 70]
        timing_res_peak_limits = [25, 75]
    
    elif md.getSensor() == "W4-RD01" and md.getBatchNumber() == 306:
        
        gain_limits = [340, 500]
        pulse_amplitude_limits = [160, 310]
        rise_time_limits = [820, 870]
        
        timing_res_peak_limits = [58, 80]
        timing_res_cfd_limits = [20, 40]
    
    elif md.getSensor() == "W4-RD01" and md.getBatchNumber() == 601:
        
        gain_limits = [330, 440]
        pulse_amplitude_limits = [140, 240]
        rise_time_limits = [1220, 1300]
        
        timing_res_peak_limits = [70, 130]
        timing_res_cfd_limits = [30, 75]
    
    elif md.getSensor() == "W4-S1022" and md.getBatchNumber() == 306:
        
        gain_limits = [20, 38]
        pulse_amplitude_limits = [35, 75]
        rise_time_limits = [600, 680]
        
        timing_res_peak_limits = [90, 160]
        timing_res_cfd_limits = [30, 80]
    
    elif md.getSensor() == "W4-S1022" and md.getBatchNumber() == 507:
        
        gain_limits = [40, 85]
        pulse_amplitude_limits = [80, 160]
        rise_time_limits = [505, 545]
        
        timing_res_peak_limits = [90, 160]
        timing_res_cfd_limits = [30, 80]
    
    elif md.getSensor() == "W4-S1022" and md.getBatchNumber() == 707:
        
        gain_limits = [35, 85]
        pulse_amplitude_limits = [80, 160]
        rise_time_limits = [525, 565]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S1061" and md.getBatchNumber() == 306:
        
        gain_limits = [35, 65]
        pulse_amplitude_limits = [85, 145]
        rise_time_limits = [490, 530]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S1061" and md.getBatchNumber() == 507:
        
        gain_limits = [35, 65]
        pulse_amplitude_limits = [80, 140]
        rise_time_limits = [535, 570]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S1061" and md.getBatchNumber() == 707:
        
        gain_limits = [30, 80]
        pulse_amplitude_limits = [70, 150]
        rise_time_limits = [540, 575]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S203" and md.getBatchNumber() == 306:
        
        gain_limits = [40, 70]
        pulse_amplitude_limits = [90, 150]
        rise_time_limits = [515, 540]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S203" and md.getBatchNumber() == 507:
        
        gain_limits = [35, 70]
        pulse_amplitude_limits = [50, 100]
        rise_time_limits = [680, 780]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S203" and md.getBatchNumber() == 707:
        
        gain_limits = [40, 80]
        pulse_amplitude_limits = [50, 110]
        rise_time_limits = [725, 830]
        
        timing_res_cfd_limits = [30, 80]
        timing_res_peak_limits = [90, 160]
    
    elif md.getSensor() == "W4-S204_6e14" and md.getBatchNumber() == 507:
        
        gain_limits = [5, 26]
        pulse_amplitude_limits = [40, 80]
        rise_time_limits = [315, 390]
        
        timing_res_cfd_limits = [36, 60]
        timing_res_peak_limits = [44, 65]
    
    elif md.getSensor() == "W4-S204_6e14" and md.getBatchNumber() == 707:
        
        gain_limits = [8, 28]
        pulse_amplitude_limits = [40, 90]
        rise_time_limits = [315, 390]
        
        timing_res_cfd_limits = [34, 48]
        timing_res_peak_limits = [40, 60]
    
    elif md.getSensor() == "W4-S215" and md.getBatchNumber() == 207:
        
        gain_limits = [70, 130]
        pulse_amplitude_limits = [160, 260]
        rise_time_limits = [490, 540]
        
        timing_res_cfd_limits = [25, 45]
        timing_res_peak_limits = [25, 50]
    
    elif md.getSensor() == "W4-S215" and md.getBatchNumber() == 507:
        
        gain_limits = [110, 210]
        pulse_amplitude_limits = [200, 330]
        rise_time_limits = [520, 590]
        
        # not used
        timing_res_cfd_limits = [20, 70]
        timing_res_peak_limits = [30, 80]
    
    elif md.getSensor() == "W4-S215" and md.getBatchNumber() == 707:
        
        gain_limits = [100, 190]
        pulse_amplitude_limits = [140, 240]
        rise_time_limits = [700, 825]
        
        # not used
        timing_res_cfd_limits = [20, 70]
        timing_res_peak_limits = [30, 80]
    
    elif md.getSensor() == "W9-LGA35" and md.getBatchNumber() == 108:
        
        # not used
        gain_limits = [30, 50]
        pulse_amplitude_limits = [60, 110]
        rise_time_limits = [415, 455]
        
        timing_res_cfd_limits = [20, 40]
        timing_res_peak_limits = [24, 46]
    
    elif md.getSensor() == "W9-LGA35" and md.getBatchNumber() == 207:
        
        gain_limits = [20, 45]
        pulse_amplitude_limits = [50, 115]
        rise_time_limits = [415, 455]
        
        # not used
        timing_res_cfd_limits = [20, 70]
        timing_res_peak_limits = [25, 75]

    # This method is modular to adapt for other batches
    else:
        
        th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
        
        pulse_amplitude_mean =  dm.exportImportROOTHistogram("pulse", "pulse_amplitude").GetFunction("Fitfcn_pulse_amplitude"+th_name).GetParameter(1)
        gain_mean =             dm.exportImportROOTHistogram("pulse", "charge").GetFunction("Fitfcn_charge"+th_name).GetParameter(1)/md.getChargeWithoutGainLayer()
        
        rise_time_mean = dm.exportImportROOTHistogram("pulse", "rise_time").GetFunction("gaus").GetParameter(1)
        timing_res_peak_mean = np.sqrt(np.power(dm.exportImportROOTHistogram("timing", "normal", "peak").GetFunction("gaus").GetParameter(2),2) - np.power(md.getSigmaSiPM(),2))
        timing_res_cfd_mean = np.sqrt(np.power(dm.exportImportROOTHistogram("timing", "normal", "cfd").GetFunction("gaus").GetParameter(2), 2) - np.power(md.getSigmaSiPM(), 2))
        
        [pulse_amplitude_limits, gain_limits, rise_time_limits, timing_res_peak_limits, timing_res_cfd_limits] = [[max(pulse_amplitude_mean-50,0), pulse_amplitude_mean+50], [max(gain_mean-30, 0), gain_mean+30], [max(rise_time_mean-30, 0), rise_time_mean+30], [max(timing_res_peak_mean-50, 0), timing_res_peak_mean+50], [max(timing_res_cfd_mean-50, 0), timing_res_cfd_mean+50]]
    
    
    limits_graph = [pulse_amplitude_limits, gain_limits, rise_time_limits, timing_res_peak_limits, timing_res_cfd_limits]

    return limits_graph
