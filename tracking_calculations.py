import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_plot as t_plot

ROOT.gROOT.SetBatch(True)

# Function appends tracking files and oscilloscope files and
# matches the sizes of them
def trackingAnalysis():

    dm.setFunctionAnalysis("tracking_analysis")
    dm.defineDataFolderPath()
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)

    print "\nStart TRACKING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:

        startTimeBatch = dm.getTime()

        # Set a condition of at least two run numbers to be analyzed
        if len(runLog) < 3:
            continue

        results_batch = []

        for index in range(0, len(runLog)):

            md.defineGlobalVariableRun(runLog[index])


            # Batch 203 have desynched events between oscilloscope and tracking
            if md.getBatchNumber() == 203:
                continue

            if not dm.checkIfFileAvailable():
                continue

            peak_values_run = dm.exportImportROOTData("pulse", "peak_value")
            charge_run = dm.exportImportROOTData("pulse", "charge")
            rise_times_run = dm.exportImportROOTData("pulse", "rise_time")
            time_difference_peak_run = dm.exportImportROOTData("timing", "linear")
            time_difference_cfd_run = dm.exportImportROOTData("timing", "linear_cfd")

            tracking_run = dm.exportImportROOTData("tracking", "tracking")

            # Slice the peak values to match the tracking files
            if len(peak_values_run) > len(tracking_run):

                peak_values_run           = np.take(peak_values_run, np.arange(0, len(tracking_run)))
                charge_run                = np.take(charge_run, np.arange(0, len(tracking_run)))
                rise_times_run            = np.take(rise_times_run, np.arange(0, len(tracking_run)))
                time_difference_peak_run  = np.take(time_difference_peak_run, np.arange(0, len(tracking_run)))
                time_difference_cfd_run   = np.take(time_difference_cfd_run, np.arange(0, len(tracking_run)))

            else:

                tracking_run = np.take(tracking_run, np.arange(0, len(peak_values_run)))


            results_batch.append([peak_values_run, charge_run, rise_times_run, tracking_run, time_difference_peak_run, time_difference_cfd_run])

        if len(results_batch) != 0:
            print "\nProducing TRACKING plots for batch " + str(md.getBatchNumber()) + ".\n"

            peak_values          = np.empty(0, dtype=results_batch[0][0].dtype)
            charge               = np.empty(0, dtype=results_batch[0][1].dtype)
            rise_times           = np.empty(0, dtype=results_batch[0][2].dtype)
            tracking             = np.empty(0, dtype=results_batch[0][3].dtype)
            time_difference_peak = np.empty(0, dtype=results_batch[0][4].dtype)
            time_difference_cfd  = np.empty(0, dtype=results_batch[0][5].dtype)

            for results_run in results_batch:
                peak_values          = np.concatenate((peak_values, results_run[0]), axis = 0)
                charge               = np.concatenate((charge, results_run[1]), axis = 0)
                rise_times           = np.concatenate((rise_times,  results_run[2]), axis = 0)
                tracking             = np.concatenate((tracking,  results_run[3]), axis = 0)
                time_difference_peak = np.concatenate((time_difference_peak,  results_run[4]), axis = 0)
                time_difference_cfd  = np.concatenate((time_difference_cfd,  results_run[5]), axis = 0)

            # For each bigger batch, this can be done once. It exports a position file which aims to center the plot
            #calculateCenterOfSensorPerBatch(peak_values, tracking)

            t_plot.trackingPlots(peak_values, charge, rise_times, time_difference_peak, time_difference_cfd, tracking)

            print "\nDone with batch",runLog[0][5],"Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"


    print "\nDone with TRACKING analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"





# Change tracking information
def changeCenterPositionSensor(tracking):

    position = dm.exportImportROOTData("tracking", "position")

    center = np.array([position[t_plot.chan][0][0], position[t_plot.chan][0][1]])

    if md.checkIfArrayPad(t_plot.chan):
    
        dist_center = getDistanceFromCenterArrayPad(position)
 
        tracking["X"] = tracking["X"] + dist_center[t_plot.chan][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[t_plot.chan][0][1]
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]

        # Rotation for W4-S204_6e14
        if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":

            theta = 4.3 * np.pi/180

            # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
            tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))

        # Rotation for W4-S215
        elif md.getNameOfSensor(t_plot.chan) == "W4-S215":

            theta = 0.6 * np.pi/180
            
              # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
            tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))

    
    else:
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]


    return tracking


def getDistanceFromCenterArrayPad(position):


    arrayPadChannels = getArrayPadChannels()
   
    numberOfPads = len(position[arrayPadChannels][0])

    if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":
        numberOfPads += 1

    pos_pad = np.zeros((numberOfPads, 2))

    for pad_no in range(0, numberOfPads):
        for dim in range(0, 2):
            
            # This is a hand-waving fix for the missing pad, to temporarily calculate the average value to find the center of the three (four) pads
            if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14" and pad_no == 3:
                pos_pad[pad_no][0] = position[arrayPadChannels][0][1][0]
                pos_pad[pad_no][1] = position[arrayPadChannels][0][0][1]
            
            else:
                pos_pad[pad_no][dim] = position[arrayPadChannels][0][pad_no][dim]


    centerArrayPadPosition = np.average(pos_pad, axis=0)

    newArrayPositions = createCenterPositionArray()

    if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":
        numberOfPads -= 1

    for index in range(0, numberOfPads):
        chan2 = arrayPadChannels[index]
        newArrayPositions[chan2][0] = pos_pad[index] - centerArrayPadPosition

    return newArrayPositions


# Create array for exporting center positions, inside tracking
def createCenterPositionArray():

    dt = (  [('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)] )
    
    return np.zeros(1, dtype = dt)


def calculateCenterOfSensorPerBatch(peak_values, tracking):

    print "Producing center positions for batch", md.getBatchNumber(), "\n"

    # Choose ranges for the tracking info
    xmin = -7000
    xmax = 7000
    ymin = 5000
    ymax = 16000
    
    bin_size = 18.5 * 2
    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)

    minEntries = 7
    
    values = [minEntries, xmin, xmax, ymin, ymax, xbin, ybin]

    position_temp = createCenterPositionArray()

    for chan in peak_values.dtype.names:

        position_temp[chan][0] = getCenterOfSensor(peak_values[chan], tracking, values)

    dm.exportImportROOTData("tracking", "position", position_temp)

    print "Done producing center position for batch", md.getBatchNumber()


def getCenterOfSensor(peak_values, tracking, values):

    [minEntries, xmin, xmax, ymin, ymax, xbin, ybin] = [i for i in values]

    mean_values = ROOT.TProfile2D("Mean value","Mean value", xbin, xmin, xmax, ybin, ymin, ymax)

    # Fill the events
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9990 and tracking['Y'][event] > -9990 and peak_values[event] != 0:
            mean_values.Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])


    # Remove bins with less than minEntries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):

            bin = mean_values.GetBin(i,j)
            num = mean_values.GetBinEntries(bin)

            if num < minEntries:
                mean_values.SetBinContent(bin, 0)
                mean_values.SetBinEntries(bin, 0)

    mean_values.ResetStats()
    
    position_temp = np.array([mean_values.GetMean(), mean_values.GetMean(2)])

    del mean_values
    
    return position_temp


def getArrayPadChannels():

    batchCategory = md.getBatchNumber()/100

    if batchCategory == 1:
        channels = ["chan4", "chan5", "chan6", "chan7"]

    elif batchCategory == 2:
        channels = ["chan3", "chan5", "chan6", "chan7"]

    elif batchCategory == 3:
        channels = ["chan4", "chan5"]

    elif batchCategory == 4:
        channels = ["chan1", "chan5", "chan6", "chan7"]

    elif batchCategory == 5 or batchCategory == 7:
        channels = ["chan5", "chan6", "chan7"]

    elif batchCategory == 6:
        channels = ["chan0", "chan1"]

    return channels


def sensorIsAnArrayPad():

    # If all sensors are considered, progress with the function
    if md.sensor == "":
        return True
    
    # Otherwise check if the sensor processed is an array pad
    else:
        chan = getArrayPadChannels()[0]

        if md.sensor == md.getNameOfSensor(chan):
            return True
        else:
            return False


def importAndAddHistogram(TH2D_object, index, export=False):

    arrayPadChannels = getArrayPadChannels()
    chan = arrayPadChannels[index]
    objectName = TH2D_object.GetName()

    fileName, headTitle = getTitleAndFileName(objectName, chan)
    
    TH2D_file = dm.exportImportROOTHistogram(fileName)
    TH2D_object_import = TH2D_file.Get(objectName)
    TH2D_object.Add(TH2D_object_import)



def getTitleAndFileName(objectName, chan):
    
    fileName = "empty"
    headTitle = "empty"

    if objectName.find("Pulse") != -1:
        graphTitle = "Pulse amplitude mean value"
        dimension_z = "V [mV]"
        folderLocation = "pulse_amplitude_mean/tracking_mean_value"
    
    
    elif objectName.find("Gain") != -1:
        graphTitle = "Gain mean value"
        dimension_z = "Gain"
        folderLocation = "gain_mean/tracking_gain_mean_value"

    
    elif objectName.find("Rise") != -1:
        graphTitle = "Rise time mean value"
        dimension_z = "t [ps]"
        folderLocation = "rise_time_mean/tracking_rise_time_mean_value"

    
    elif objectName.find("peak") != -1:
        graphTitle = "Timing resolution (peak)"
        dimension_z = "\sigma_{t} [ps]"
        folderLocation = "time_resolution/peak/tracking_time_resolution_peak"


    elif objectName.find("cfd") != -1:
    
        graphTitle = "Timing resolution (CFD)"
        dimension_z = "\sigma_{t} [ps]"
        folderLocation = "time_resolution/cfd/tracking_time_resolution_cfd"

    
    elif objectName.find("Efficiency") != -1:
        graphTitle = "Efficiency"
        dimension_z = "Efficiency (%)"
        folderLocation = "efficiency/tracking_efficiency"

    
    elif objectName.find("Inefficiency") != -1:
        graphTitle = "Inefficiency"
        dimension_z = "Inefficiency (%)"
        folderLocation = "inefficiency/tracking_inefficiency"


    headTitle = graphTitle + " - " + md.getNameOfSensor(chan) + ", T = " + str(md.getTemperature()) + " \circ C, U = " + str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V; X [\mum] ; Y [\mum] ; " + dimension_z
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder() + "/" + md.getNameOfSensor(chan)+ "/tracking/" + folderLocation + "_" + str(md.getBatchNumber()) + "_" + chan + "_" + str(md.getNameOfSensor(chan)) + ".pdf"
    

    if array_pad_export:
        fileName = fileName.replace(".pdf", "_array.pdf")
        

    return fileName, headTitle


def drawLines(line_extension=0):

    ranges, center_positions = findSelectionRange()

    x1 = ranges[0][0]
    x2 = ranges[0][1]
    y1 = ranges[1][0]
    y2 = ranges[1][1]

    # Lines which selects the area in y for projection in x
    line_y1 = ROOT.TLine(x1-line_extension, y1, x2+line_extension, y1)
    line_y2 = ROOT.TLine(x1-line_extension, y2, x2+line_extension, y2)

    # Lines which selects the area in x for projection in y
    line_x1 = ROOT.TLine(x1, y1-line_extension, x1, y2+line_extension)
    line_x2 = ROOT.TLine(x2, y1-line_extension, x2, y2+line_extension)
    
    line_y1.SetLineWidth(2)
    line_y2.SetLineWidth(2)
    line_x1.SetLineWidth(2)
    line_x2.SetLineWidth(2)
    
    return [line_y1, line_y2, line_x1, line_x2]


def findSelectionRange():
    
    position = dm.exportImportROOTData("tracking", "position")
    
    
    # In case of array pads, refer to the center of the pad
    if md.checkIfArrayPad(md.chan_name):
    
        center_position  = (getDistanceFromCenterArrayPad(position)[md.chan_name])[0]
    
    # otherwise, refer from origo with predefined structured array
    else:
        center_position = (createCenterPositionArray()[md.chan_name])[0]

    # Distance from the center of the pad and 350 um from the center
    projection_cut = 350

    # This is a correction for the irradiated array pad to center the selection of the bulk for efficiency calculation
    if md.getNameOfSensor(md.chan_name) == "W4-S204_6e14":
        
        if md.chan_name == "chan5":
            center_position = [-530, -575]
        
        elif md.chan_name == "chan6":
            center_position = [530, 500]
            
        elif md.chan_name == "chan7":
            center_position = [-530, 500]
        

    x1 = center_position[0] - projection_cut
    x2 = center_position[0] + projection_cut
    y1 = center_position[1] - projection_cut
    y2 = center_position[1] + projection_cut
    

    return np.array([[x1, x2], [y1, y2]]), center_position


def removeBin(bin, time_diff, minEntries):

    num = time_diff.GetBinEntries(bin)
    
    if num < minEntries:
        time_diff.SetBinContent(bin, 0)
        time_diff.SetBinEntries(bin, 0)


def fillTimeResBin(bin, time_diff, time_res, entries_per_bin):

    num = time_diff.GetBinEntries(bin)

    if num > entries_per_bin:

        sigma_convoluted = time_diff.GetBinError(bin)
        sigma_DUT = np.sqrt(np.power(sigma_convoluted, 2) - np.power(md.getSigmaSiPM(), 2))
        time_res.SetBinContent(bin, sigma_DUT)


def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
