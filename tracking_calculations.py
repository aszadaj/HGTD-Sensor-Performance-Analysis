import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_plot as t_plot
import pulse_plot as p_plot
import timing_plot as tim_plot


def fillTHObjects(numpy_arrays, TH2_objects_fill, tracking, th1_limits):
    
    [peak_value_mean_TH2F, gain_mean_TH2F, rise_time_mean_TH2F, time_difference_peak_TH2F, time_difference_cfd_TH2F, timing_peak_TH2F, timing_cfd_TH2F] = [i for i in TH2_objects_fill]
    
    [xbin, ybin, xbin_timing, ybin_timing, distance_x, distance_y] = [i for i in th1_limits]
    
    stripNumpyArrays(numpy_arrays)
    
    # Fill all objects except timing resolution
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):
            for index in range(0, len(numpy_arrays)):
                if numpy_arrays[index][event] != 0:
                    TH2_objects_fill[index].Fill(tracking['X'][event], tracking['Y'][event], numpy_arrays[index][event])


    # Remove bins with few entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = peak_value_mean_TH2F.GetBin(i,j)
            removeBin(bin, peak_value_mean_TH2F)
            removeBin(bin, rise_time_mean_TH2F)
            removeBin(bin, gain_mean_TH2F)

        peak_value_mean_TH2F.ResetStats()
        rise_time_mean_TH2F.ResetStats()
        gain_mean_TH2F.ResetStats()

    
    # Fill timing resolution bins
    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
            
            bin = time_difference_peak_TH2F.GetBin(i,j)
            fillTimeResBin(bin, time_difference_peak_TH2F, timing_peak_TH2F)
            fillTimeResBin(bin, time_difference_cfd_TH2F, timing_cfd_TH2F)


def fillEfficiencyObjects(LGAD_TH2F, MIMOSA_TH2F, tracking, peak_values, distance_x, distance_y, xbin, ybin):

    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):

            # Total events
            MIMOSA_TH2F.Fill(tracking['X'][event], tracking['Y'][event], 1)

            # Passed events
            if peak_values[event] != 0:
                LGAD_TH2F.Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = LGAD_TH2F.GetBin(i,j)
            num_LGAD = LGAD_TH2F.GetBinContent(bin)
            
            if num_LGAD < t_plot.bin_entries:
                LGAD_TH2F.SetBinContent(bin, 0)
                MIMOSA_TH2F.SetBinContent(bin, 0)

    LGAD_TH2F.ResetStats()
    MIMOSA_TH2F.ResetStats()


def fillInefficiencyAndProjectionObjects(efficiency_TH2F, inefficiency_TH2F, projectionX_th1d, projectionY_th1d, xbin, ybin):
    
    distance_projection, center_positions = findSelectionRange()

    # Define lower and upper limits bins
    bin_x_low = efficiency_TH2F.GetXaxis().FindBin(distance_projection[0][0])
    bin_x_high = efficiency_TH2F.GetXaxis().FindBin(distance_projection[0][1])
    bin_y_low = efficiency_TH2F.GetYaxis().FindBin(distance_projection[1][0])
    bin_y_high = efficiency_TH2F.GetYaxis().FindBin(distance_projection[1][1])
    
    bin_limits = np.array([bin_x_low, bin_x_high, bin_y_low, bin_y_high])
    
    efficiency_bulk_data = np.array([])
    
    # Loop through each bin, to obtain inefficiency, and fill projection objects
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = efficiency_TH2F.GetBin(i,j)
            eff = efficiency_TH2F.GetBinContent(bin)
            
            if eff > 0:
                inefficiency_TH2F.SetBinContent(bin, 100-eff)
                
                if (bin_limits[0] <= i <= bin_limits[1]) and (bin_limits[2] <= j <= bin_limits[3]):
                    
                    efficiency_bulk_data = np.concatenate((efficiency_bulk_data, np.array([eff])))
            
            if eff == 100:
                inefficiency_TH2F.SetBinContent(bin, 0.001)
            
            
            # Fill projection Y efficiency values within x-limits
            if bin_limits[0] <= i <= bin_limits[1]:
                y = efficiency_TH2F.GetYaxis().GetBinCenter(j)
                projectionY_th1d.Fill(y, eff)
            
            # Fill projection X efficiency values within y-limits
            if bin_limits[2] <= j <= bin_limits[3]:
                x = efficiency_TH2F.GetXaxis().GetBinCenter(i)
                projectionX_th1d.Fill(x, eff)

    # Additional comment: bin_limits marks the lines for which the selection of the
    # projection for each dimension. Vertical limits are for the Y-projection, where
    # horizontal is for X-projection. Then for each "line of bins" are projected by
    # filling within the limits. TProfile objects then calculate the mean in each filled
    # line. The point here is to see how the edges increases

    efficiency_bulk = [np.mean(efficiency_bulk_data), np.std(efficiency_bulk_data)]
    dm.exportImportROOTData("tracking", "efficiency", np.array(efficiency_bulk))


# Import results from already exported histograms to strip extreme values. Set a 5 sigma level on the standard deviation from the histogram.
def stripNumpyArrays(numpy_arrays):
    
    # These are names of the TH1D objects declared in plot .py-files
    objectNames = ["Pulse amplitude"+" "+str(md.getBatchNumber())+" "+md.chan_name,"Charge"+" "+str(md.getBatchNumber())+" "+md.chan_name,"Rise time"+" "+str(md.getBatchNumber())+" "+md.chan_name,"Linear time difference "+str(md.getBatchNumber())+" "+md.chan_name,"Linear time difference "+str(md.getBatchNumber())+" "+md.chan_name]

    N = 5
    
    # Strip pulse amplitude values higher than 390 mV
    numpy_arrays[0][numpy_arrays[0] > 390] = 0
    
    for index in range(2, len(numpy_arrays)):

        if t_plot.var_names[index][1] == "rise_time":
            
            [headTitle, xAxisTitle, yAxisTitle, fileName] = p_plot.getPlotAttributes(t_plot.var_names[index][1])
        
        else:
            
            [headTitle, xAxisTitle, yAxisTitle, fileName] = tim_plot.getPlotAttributes(t_plot.var_names[index][1])
            

        TFile = dm.exportImportROOTHistogram(fileName)
        THistogram = TFile.Get(objectNames[index])
        
        mean = THistogram.GetMean()
        sigma = THistogram.GetStdDev()
        
        numpy_arrays[index][mean - N * sigma > numpy_arrays[index]] = 0
        numpy_arrays[index][mean + N * sigma < numpy_arrays[index]] = 0



# Change tracking information
def changeCenterPositionSensor(tracking):

    position = dm.exportImportROOTData("tracking", "position")

    center = np.array([position[md.chan_name][0][0], position[md.chan_name][0][1]])
    theta = 0
    
    # Center the pad or array
    tracking["X"] = tracking["X"] - center[0]
    tracking["Y"] = tracking["Y"] - center[1]

    if md.checkIfArrayPad():
    
        # Plot each pad to its position
        dist_center = getDistanceFromCenterArrayPad(position)
        tracking["X"] = tracking["X"] + dist_center[md.chan_name][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[md.chan_name][0][1]
    
    
    # Rotation for W4-S204_6e14
    if md.getSensor() == "W4-S204_6e14":

        theta = 4.3

    # Rotation or W4-S215
    elif md.getSensor() == "W4-S215" and md.checkIfArrayPad():
        
        theta = 0.6 # was 0.6
    
    # Rotation or W4-S215
    elif md.getSensor() == "W4-S215" and md.getBatchNumber()/100 == 5:
        
        theta = 1.5

    # Rotation or W4-S215
    elif md.getSensor() == "W4-S215" and md.getBatchNumber()/100 == 7:
        
        theta = 1.2

    
    if theta != 0:
        # Use the rotation matrix around z
        theta *= np.pi/180
        tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
        tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))


    return tracking


def getDistanceFromCenterArrayPad(position):

    arrayPadChannels = getArrayPadChannels()
   
    numberOfPads = len(position[arrayPadChannels][0])

    if md.getSensor() == "W4-S204_6e14":
        numberOfPads += 1

    pos_pad = np.zeros((numberOfPads, 2))

    for pad_no in range(0, numberOfPads):
        for dim in range(0, 2):
            
            # This is a hand-waving fix for the missing pad, to temporarily calculate the average value to find the center of the three (four) pads
            if md.getSensor() == "W4-S204_6e14" and pad_no == 3:
                pos_pad[pad_no][0] = position[arrayPadChannels][0][1][0]
                pos_pad[pad_no][1] = position[arrayPadChannels][0][0][1]
            
            else:
                pos_pad[pad_no][dim] = position[arrayPadChannels][0][pad_no][dim]


    centerArrayPadPosition = np.average(pos_pad, axis=0)

    newArrayPositions = np.zeros(1, dtype = dm.getDTYPETrackingPosition())

    if md.getSensor() == "W4-S204_6e14":
        numberOfPads -= 1

    for index in range(0, numberOfPads):
        chan2 = arrayPadChannels[index]
        newArrayPositions[chan2][0] = pos_pad[index] - centerArrayPadPosition

    return newArrayPositions


def calculateCenterOfSensorPerBatch(peak_values, tracking):

    # Calculate position for largest batches
    if md.getBatchNumber() not in [101, 207, 306, 401, 507, 601, 707]:
        return 0
    
    global canvas_center
    
    canvas_center = ROOT.TCanvas("c1", "c1")
    
    print "\nCalculating CENTER POSITIONS for batch", md.getBatchNumber(), "\n"

    position_temp = np.zeros(1, dtype = dm.getDTYPETrackingPosition())

    for chan in peak_values.dtype.names:
        md.setChannelName(chan)

        position_temp[chan][0] = getCenterOfSensor(peak_values[chan], tracking)

    dm.exportImportROOTData("tracking", "position", position_temp)

    print "DONE producing CENTER POSITIONS for batch", md.getBatchNumber(), "\n"


def getCenterOfSensor(peak_values, tracking):
    
    bin_size = 18.5
    
    # Choose ranges to center the DUTs depending on batch (the SiPM is larger, therefore the mean values of it are not exact)
    if md.getBatchNumber() == 101:
        [xmin, xmax, ymin, ymax, minEntries] = [-1500, 1500, 12000, 14500, 10]
    
    elif md.getBatchNumber() == 207:
        [xmin, xmax, ymin, ymax, minEntries] = [-1000, 1500, 11500, 14500, 20]

    elif md.getBatchNumber() == 306:
        [xmin, xmax, ymin, ymax, minEntries] = [-4500, -1000, 11000, 14000, 20]
    
    elif md.getBatchNumber() == 401:
        [xmin, xmax, ymin, ymax, minEntries] = [-4000, -1200, 10500, 13500, 10]

    elif md.getBatchNumber() == 507:
        [xmin, xmax, ymin, ymax, minEntries] = [-3000, 1000, 10000, 13500, 15]
    
    elif md.getBatchNumber() == 601:
        [xmin, xmax, ymin, ymax, minEntries] = [-1200, 300, 10000, 13000, 20]
    
    elif md.getBatchNumber() == 707:
        [xmin, xmax, ymin, ymax, minEntries] = [-3000, 800, 10000, 13500, 5]


    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)
    
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
            removeBin(bin, mean_values, minEntries)

    mean_values.ResetStats()

    # Calculate the mean value for each DUT
    position_temp = np.array([mean_values.GetMean(), mean_values.GetMean(2)])

    # Print the graph to estimate if the positions are correct
    mean_values.Draw("COLZ")
    canvas_center.Update()
    position_plots_filePath = dm.getSourceFolderPath() + dm.getDataSourceFolder() + "/positions/"+md.getSensor()+"_"+str(md.getBatchNumber())+"_"+md.chan_name+"_"+".pdf"
    canvas_center.Print(position_plots_filePath)
    
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

# Check if the sensor processed is an array pad
def sensorIsAnArrayPad():

    bool = True

    if md.sensor != "":
        md.setChannelName(getArrayPadChannels()[0])
        
        if md.sensor != md.getSensor():
            bool = False

    return bool


def importAndAddHistogram(TH2_object, index):

    arrayPadChannels = getArrayPadChannels()
    chan = arrayPadChannels[index]
    
    objectName = TH2_object.GetName()
    fileName, headTitle = getTitleAndFileName(objectName, chan)
    
    TH2_file = dm.exportImportROOTHistogram(fileName)
    TH2_object_import = TH2_file.Get(objectName)
    TH2_object.Add(TH2_object_import)


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


    elif objectName.find("CFD") != -1:
    
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


    headTitle = graphTitle + " - " + md.getSensor() + ", T = " + str(md.getTemperature()) + " \circ C, U = " + str(md.getBiasVoltage()) + " V; X [\mum] ; Y [\mum] ; " + dimension_z
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder() + "/" + md.getSensor()+ "/tracking/" + folderLocation + "_" + str(md.getBatchNumber()) + "_" + chan + "_" + str(md.getSensor()) + ".pdf"
    

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
    if md.checkIfArrayPad():
    
        center_position  = (getDistanceFromCenterArrayPad(position)[md.chan_name])[0]
    
    # otherwise, refer from origo with predefined structured array
    else:
        center_position = (np.zeros(1, dtype = dm.getDTYPETrackingPosition())[md.chan_name])[0]

    # Distance from the center of the pad and 350 um from the center
    projection_cut = 350

    # This is a correction for the irradiated array pad to center the selection of the bulk for efficiency calculation
    if md.getSensor() == "W4-S204_6e14":
        
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


def removeBin(bin, time_diff, minEntries=0):

    if minEntries == 0:
        minEntries = t_plot.bin_entries
    
    if time_diff.GetBinEntries(bin) < minEntries:
        time_diff.SetBinContent(bin, 0)
        time_diff.SetBinEntries(bin, 0)


def fillTimeResBin(bin, time_diff, time_res):

    if time_diff.GetBinEntries(bin) > t_plot.bin_entries_timing:

        sigma_DUT = np.sqrt(np.power(time_diff.GetBinError(bin), 2) - np.power(md.getSigmaSiPM(), 2))
        time_res.SetBinContent(bin, sigma_DUT)


def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
